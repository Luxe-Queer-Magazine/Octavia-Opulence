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

from transformers import (
    # AutoModelForCausalLM, # No longer needed for loading if using Unsloth
    AutoTokenizer,
    TrainingArguments,
    set_seed,
    Trainer, # Keep standard Trainer for now
)
from datasets import load_dataset
from peft import LoraConfig # Keep for defining the config object
# from peft import prepare_model_for_kbit_training # No longer needed if using Unsloth 4bit loading

logger = logging.getLogger(__name__)

# ... (Keep your Dataclasses: ModelArguments, DataArguments, TrainingConfig) ...
# ... (Keep load_training_config, format_instruction, preprocess_function) ...

def main():
    parser = argparse.ArgumentParser()
    # ... (Keep parser arguments) ...
    args = parser.parse_args()

    # Load training configuration
    training_config = load_training_config(args.config_path)

    # Set seed for reproducibility
    set_seed(training_config.seed)

    # --- CORRECTED MODEL & TOKENIZER LOADING ---
    print("Loading model and tokenizer with Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = args.base_model,
        # You might want max_seq_length here, check Unsloth docs
        # max_seq_length = 2048, # Example
        dtype = None, # Autodetect or torch.bfloat16/torch.float16
        load_in_4bit = True, # Explicitly use 4bit based on your goal
        # token = "hf_...", # Add token if needed
        device_map = "auto", # Unsloth handles device mapping
        # trust_remote_code=True, # Usually not needed unless model requires it
    )
    print("Model and tokenizer loaded.")

    # Ensure pad token is set (Unsloth might do this, but good practice)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        print("Set pad_token to eos_token")
    # ---------------------------------------------

    # --- REMOVE prepare_model_for_kbit_training ---
    # model = prepare_model_for_kbit_training(model) # REMOVE THIS LINE
    # ---------------------------------------------

    # Configure LoRA (Your existing code without target_modules is correct here)
    print("Configuring LoRA...")
    lora_config = LoraConfig(
        r=training_config.lora.get("r", 16),
        lora_alpha=training_config.lora.get("alpha", 32),
        lora_dropout=training_config.lora.get("dropout", 0.05),
        bias="none",
        task_type="CAUSAL_LM",
        # NO target_modules needed for Unsloth auto-detect on Gemma
    )
    print("LoRA Configured.")

    # --- CORRECTED PEFT APPLICATION (Ensure using the model loaded by Unsloth) ---
    print("Applying PEFT adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        lora_config
    )
    print("PEFT adapters applied.")
    # --------------------------------------------------------------------------

    # Load and preprocess dataset (Your existing code is likely fine here)
    print("Loading dataset...")
    try:
        # ... (Your dataset loading logic) ...
        dataset = load_dataset("json", data_files=data_files)
        print("Dataset loaded.")

        print("Preprocessing dataset...")
        tokenized_dataset = dataset.map(
            lambda examples: preprocess_function(examples, tokenizer),
            batched=True,
            # Check if 'train' split always exists, might need dynamic key
            remove_columns=list(dataset.values())[0].column_names,
        )
        print("Dataset preprocessed.")
    except Exception as e:
        logger.error(f"Error loading or processing dataset: {e}")
        return # Exit if dataset fails

    # Set up training arguments (Your existing code is likely fine here)
    # Make sure fp16 is set correctly based on training_config
    training_args = TrainingArguments(
        # ... (Your TrainingArguments setup, ensure fp16=training_config.fp16 is set) ...
        fp16=training_config.fp16, # Correct place for fp16 setting
        # ... (rest of your args) ...
        output_dir=args.output_dir,
        per_device_train_batch_size=training_config.train_batch_size,
        gradient_accumulation_steps=training_config.gradient_accumulation_steps,
        warmup_steps=training_config.warmup_steps,
        # num_train_epochs=training_config.num_train_epochs, # Often use max_steps instead
        max_steps = 100, # Example: Use max_steps instead of epochs for testing
        learning_rate=training_config.learning_rate,
        logging_steps=training_config.logging_steps,
        save_steps=training_config.save_steps,
        optim = "adamw_8bit", # Recommended optimizer with Unsloth 4bit
        save_total_limit = training_config.save_total_limit,
        seed = training_config.seed,
        # Add evaluation args if needed
    )

    # Initialize Trainer (Using standard Trainer for now)
    print("Initializing Trainer...")
    trainer = Trainer( # Explicitly use transformers.Trainer if not changing yet
        model=model,
        tokenizer=tokenizer, # Pass tokenizer to Trainer
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        # eval_dataset=tokenized_dataset.get("validation", None), # Add eval dataset if present
        # data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False), # Often needed
    )
    print("Trainer initialized.")

    # Train model
    print("Starting training...")
    trainer.train()
    print("Training finished.")

    # Save model
    print(f"Saving model to {args.output_dir}...")
    # Unsloth might have specific saving recommendations, check their docs,
    # but standard PEFT save should work.
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Model saved to {args.output_dir}")

if __name__ == "__main__":
    main()
