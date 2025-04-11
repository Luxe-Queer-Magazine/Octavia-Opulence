#!/usr/bin/env python
# coding=utf-8

import json
import argparse
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict

# --- CORRECTED IMPORT ORDER ---
import torch
from unsloth import FastLanguageModel # Import Unsloth early
# ----------------------------

# Imports need to be at the top level
from transformers import (
    AutoTokenizer,
    TrainingArguments,
    set_seed,
    Trainer,
)
from datasets import load_dataset
from peft import LoraConfig

logger = logging.getLogger(__name__)

# --- Define Dataclasses and Helper Functions Here ---
# (Keep your ModelArguments, DataArguments, TrainingConfig dataclasses)
# (Keep load_training_config, format_instruction, preprocess_function functions)
@dataclass
class ModelArguments:
    base_model: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    load_in_4bit: bool = field(
        default=True,
        metadata={"help": "Whether to load the model in 4-bit mode"}
    )

@dataclass
class DataArguments:
    data_path: str = field(
        metadata={"help": "Path to the training data."}
    )
    eval_data_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the evaluation data."}
    )

@dataclass
class TrainingConfig:
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
    # Handle potential boolean string values from JSON if needed
    config_dict['fp16'] = str(config_dict.get('fp16', True)).lower() == 'true'
    config_dict['load_best_model_at_end'] = str(config_dict.get('load_best_model_at_end', True)).lower() == 'true'
    config_dict['greater_is_better'] = str(config_dict.get('greater_is_better', False)).lower() == 'true'
    return TrainingConfig(**config_dict)

def format_instruction(example):
    """Format the instruction, input, and output into a prompt."""
    # Simplified formatting - adjust based on your actual data structure
    # This assumes 'instruction', 'input', 'output' keys exist
    prompt = f"### Instruction:\n{example.get('instruction', '')}"
    if example.get("input"):
        prompt += f"\n\n### Input:\n{example['input']}"
    prompt += f"\n\n### Response:\n{example.get('output', '')}" # Include output for training
    return prompt

def preprocess_function(examples, tokenizer):
    """Preprocess the examples for training."""
    # This needs to match your data structure and formatting goal
    # Assuming SFTTrainer might be used later, often aims for a single 'text' field
    # If using standard Trainer, you need 'input_ids' and 'labels'

    # Option 1: Formatting for SFTTrainer (requires 'text' field)
    # texts = [format_instruction(ex) for ex in examples] # Needs adaptation if examples is dict of lists
    # tokenized_examples = tokenizer(texts, truncation=True, padding="max_length", max_length=tokenizer.model_max_length)
    # return tokenized_examples

    # Option 2: Formatting for standard Trainer (modify format_instruction/logic)
    # This requires format_instruction to output the prompt correctly,
    # and you need to handle labels carefully (masking prompt tokens)
    # The original preprocess function was attempting this, let's adapt it:

    prompts = [format_instruction({"instruction": instruction, "input": inp, "output": out})
               for instruction, inp, out in zip(examples["instruction"], examples.get("input", [None]*len(examples["instruction"])), examples["output"])]

    tokenized_examples = tokenizer(
        prompts,
        truncation=True,
        padding="max_length",
        max_length=tokenizer.model_max_length, # Ensure tokenizer has this set
        # return_tensors="pt", # Trainer handles tensor conversion
    )
    # For standard Trainer, labels are usually same as input_ids for LM fine-tuning
    tokenized_examples["labels"] = tokenized_examples["input_ids"].copy()
    return tokenized_examples

# --- Main Execution Logic ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, required=True, help="Base model to fine-tune")
    parser.add_argument("--data_path", type=str, required=True, help="Path to training data JSONL")
    parser.add_argument("--eval_data_path", type=str, default=None, help="Path to evaluation data JSONL")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for model")
    parser.add_argument("--config_path", type=str, required=True, help="Path to training configuration JSON")
    args = parser.parse_args() # Parse arguments HERE

    # **** ALL THE FOLLOWING CODE MOVED INSIDE main() ****

    # Load training configuration using the parsed arg
    training_config = load_training_config(args.config_path)

    # Set seed for reproducibility
    set_seed(training_config.seed)

    # --- CORRECTED MODEL & TOKENIZER LOADING ---
    print("Loading model and tokenizer with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = args.base_model, # Use parsed arg
        # You might want max_seq_length here, check Unsloth docs
        max_seq_length = 2048, # Example, make configurable if needed
        dtype = None, # Autodetect or torch.bfloat16/torch.float16
        load_in_4bit = True, # Explicitly use 4bit based on your goal
        # token = "hf_...", # Add token if needed
        device_map = "auto", # Unsloth handles device mapping
    )
    print("Model and tokenizer loaded.")

    # Ensure pad token is set
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right" # Fix weird overflow issue with fp16 training
        print(f"Set pad_token to {tokenizer.pad_token} and padding_side to right")

    # Set model_max_length if not present
    if not hasattr(tokenizer, 'model_max_length') or tokenizer.model_max_length > 2048: # Example limit
         tokenizer.model_max_length = 2048
         print(f"Set tokenizer.model_max_length to {tokenizer.model_max_length}")


    # Configure LoRA
    print("Configuring LoRA...")
    lora_config = LoraConfig(
        r=training_config.lora.get("r", 16),
        lora_alpha=training_config.lora.get("alpha", 32),
        lora_dropout=training_config.lora.get("dropout", 0.05),
        bias="none",
        task_type="CAUSAL_LM",
        # No target_modules needed for Unsloth auto-detect
    )
    print("LoRA Configured.")

    # Apply PEFT adapters
    print("Applying PEFT adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        lora_config
    )
    print("PEFT adapters applied.")
    model.print_trainable_parameters() # Good sanity check

    # Load and preprocess dataset
    print("Loading dataset...")
    try:
        data_files = {"train": args.data_path} # Use parsed arg
        if args.eval_data_path: # Use parsed arg
            data_files["validation"] = args.eval_data_path
        dataset = load_dataset("json", data_files=data_files)
        print("Dataset loaded:", dataset)

        print("Preprocessing dataset...")
        # Ensure preprocess function is defined above or imported
        tokenized_dataset = dataset.map(
            lambda examples: preprocess_function(examples, tokenizer),
            batched=True,
            # Dynamically get column names from the first available split
            remove_columns=list(dataset.values())[0].column_names,
        )
        print("Dataset preprocessed:", tokenized_dataset)
    except Exception as e:
        logger.error(f"Error loading or processing dataset: {e}", exc_info=True) # Add traceback
        return # Exit if dataset fails

    # Set up training arguments
    print("Setting up Training Arguments...")
    training_args = TrainingArguments(
        per_device_train_batch_size = training_config.train_batch_size,
        gradient_accumulation_steps = training_config.gradient_accumulation_steps,
        warmup_steps = training_config.warmup_steps,
        # num_train_epochs = training_config.num_train_epochs, # Prefer max_steps
        max_steps = 100, # Use max_steps for quicker testing initially
        learning_rate = training_config.learning_rate,
        fp16 = training_config.fp16, # Use boolean value from config
        logging_steps = training_config.logging_steps,
        optim = "adamw_8bit", # Recommended optimizer
        weight_decay = training_config.weight_decay,
        lr_scheduler_type = "linear", # Example scheduler
        seed = training_config.seed,
        output_dir = args.output_dir, # Use parsed arg
        evaluation_strategy = training_config.evaluation_strategy if "validation" in tokenized_dataset else "no",
        eval_steps = training_config.eval_steps if "validation" in tokenized_dataset else None,
        save_steps = training_config.save_steps,
        save_total_limit = training_config.save_total_limit,
        load_best_model_at_end = training_config.load_best_model_at_end if "validation" in tokenized_dataset else False,
        metric_for_best_model = training_config.metric_for_best_model if "validation" in tokenized_dataset else None,
        greater_is_better = training_config.greater_is_better if "validation" in tokenized_dataset else None,
        report_to="tensorboard", # Or "wandb", etc.
    )
    print("Training Arguments set up.")

    # Initialize Trainer
    print("Initializing Trainer...")
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset.get("validation"), # Handles None if no eval split
        # data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False), # Add if needed
    )
    print("Trainer initialized.")

    # Train model
    print("Starting training...")
    trainer.train()
    print("Training finished.")

    # Save model
    print(f"Saving model to {args.output_dir}...")
    # Use PEFT's save_pretrained for adapters + config
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    # Optionally save the base model config too
    # model.base_model.save_pretrained(args.output_dir) # If needed for merging later
    print(f"Model saved to {args.output_dir}")

# --- Entry Point ---
if __name__ == "__main__":
    # Configure logging (optional but good practice)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main() # Call the main function which now contains all the logic
