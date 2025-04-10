#!/usr/bin/env python
# coding=utf-8

import os
import json
import argparse
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List

import torch
import transformers
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    HfArgumentParser,
    TrainingArguments,
    set_seed,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset

logger = logging.getLogger(__name__)

@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune.
    """
    base_model: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    load_in_8bit: bool = field(
        default=False,
        metadata={"help": "Whether to load the model in 8-bit mode"}
    )
    load_in_4bit: bool = field(
        default=True,
        metadata={"help": "Whether to load the model in 4-bit mode"}
    )
    trust_remote_code: bool = field(
        default=False,
        metadata={"help": "Whether to trust remote code when loading the model"}
    )

@dataclass
class DataArguments:
    """
    Arguments pertaining to what data we are going to input our model for training and evaluation.
    """
    data_path: str = field(
        metadata={"help": "Path to the training data."}
    )
    eval_data_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the evaluation data."}
    )

@dataclass
class TrainingConfig:
    """
    Arguments pertaining to training configuration loaded from JSON.
    """
    train_batch_size: int = 8
    eval_batch_size: int = 8
    num_train_epochs: int = 3
    learning_rate: float = 2e-5
    warmup_steps: int = 100
    weight_decay: float = 0.01
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1.0
    gradient_accumulation_steps: int = 4
    seed: int = 42
    fp16: bool = True
    lora: Dict = field(default_factory=dict)
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    save_steps: int = 500
    logging_steps: int = 100
    save_total_limit: int = 3
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    greater_is_better: bool = False

def load_training_config(config_path: str) -> TrainingConfig:
    """Load training configuration from JSON file."""
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    return TrainingConfig(**config_dict)

def format_instruction(example):
    """Format the instruction, input, and output into a prompt."""
    if example.get("input"):
        return f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
    else:
        return f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"

def preprocess_function(examples, tokenizer):
    """Preprocess the examples for training."""
    # Format the examples
    prompts = [format_instruction({"instruction": instruction, "input": inp, "output": out}) 
               for instruction, inp, out in zip(examples["instruction"], examples["input"], examples["output"])]
    
    # Tokenize the examples
    tokenized_examples = tokenizer(
        prompts,
        truncation=True,
        padding="max_length",
        max_length=tokenizer.model_max_length,
        return_tensors="pt",
    )
    
    # Create labels (same as input_ids, as we're doing causal language modeling)
    tokenized_examples["labels"] = tokenized_examples["input_ids"].clone()
    
    return tokenized_examples

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, required=True, help="Base model to fine-tune")
    parser.add_argument("--data_path", type=str, required=True, help="Path to training data")
    parser.add_argument("--eval_data_path", type=str, default=None, help="Path to evaluation data")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for model")
    parser.add_argument("--config_path", type=str, required=True, help="Path to training configuration")
    args = parser.parse_args()
    
    # Load training configuration
    training_config = load_training_config(args.config_path)
    
    # Set seed for reproducibility
    set_seed(training_config.seed)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        load_in_8bit=False,
        load_in_4bit=True,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=training_config.lora.get("r", 16),
        lora_alpha=training_config.lora.get("alpha", 32),
        lora_dropout=training_config.lora.get("dropout", 0.05),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=training_config.lora.get("target_modules", ["q_proj", "v_proj"]),
    )
    
    # Apply LoRA to model
    model = get_peft_model(model, lora_config)
    
    # Load dataset
    data_files = {"train": args.data_path}
    if args.eval_data_path:
        data_files["validation"] = args.eval_data_path
    
    dataset = load_dataset("json", data_files=data_files)
    
    # Preprocess dataset
    tokenized_dataset = dataset.map(
        lambda examples: preprocess_function(examples, tokenizer),
        batched=True,
        remove_columns=dataset["train"].column_names,
    )
    
    # Set up training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=training_config.train_batch_size,
        per_device_eval_batch_size=training_config.eval_batch_size,
        num_train_epochs=training_config.num_train_epochs,
        learning_rate=training_config.learning_rate,
        warmup_steps=training_config.warmup_steps,
        weight_decay=training_config.weight_decay,
        adam_epsilon=training_config.adam_epsilon,
        max_grad_norm=training_config.max_grad_norm,
        gradient_accumulation_steps=training_config.gradient_accumulation_steps,
        evaluation_strategy=training_config.evaluation_strategy if "validation" in tokenized_dataset else "no",
        eval_steps=training_config.eval_steps if "validation" in tokenized_dataset else None,
        save_steps=training_config.save_steps,
        logging_steps=training_config.logging_steps,
        save_total_limit=training_config.save_total_limit,
        load_best_model_at_end=training_config.load_best_model_at_end if "validation" in tokenized_dataset else False,
        metric_for_best_model=training_config.metric_for_best_model,
        greater_is_better=training_config.greater_is_better,
        fp16=training_config.fp16,
        seed=training_config.seed,
        report_to="tensorboard",
    )
    
    # Initialize Trainer
    trainer = transformers.Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset.get("validation", None),
    )
    
    # Train model
    trainer.train()
    
    # Save model
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    
    print(f"Model saved to {args.output_dir}")

if __name__ == "__main__":
    main()
