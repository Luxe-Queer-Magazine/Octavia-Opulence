#!/usr/bin/env python
# coding=utf-8

import os
import json
import argparse
import pandas as pd
from datasets import Dataset

def format_instruction(example):
    """Format the instruction, input, and output into a prompt."""
    if example.get("input"):
        return f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
    else:
        return f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True, help="Input file path (CSV, JSON, or JSONL)")
    parser.add_argument("--output_file", type=str, required=True, help="Output file path (JSONL)")
    parser.add_argument("--instruction_column", type=str, default="instruction", help="Column name for instruction")
    parser.add_argument("--input_column", type=str, default="input", help="Column name for input")
    parser.add_argument("--output_column", type=str, default="output", help="Column name for output")
    parser.add_argument("--split_ratio", type=float, default=0.1, help="Ratio of data to use for validation")
    parser.add_argument("--create_validation", action="store_true", help="Whether to create a validation set")
    args = parser.parse_args()
    
    print(f"Processing input file: {args.input_file}")
    
    # Determine file type and load data
    file_ext = os.path.splitext(args.input_file)[1].lower()
    
    if file_ext == '.csv':
        df = pd.read_csv(args.input_file)
    elif file_ext == '.json':
        with open(args.input_file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
    elif file_ext == '.jsonl':
        data = []
        with open(args.input_file, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        df = pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    # Validate columns
    required_columns = [args.instruction_column, args.output_column]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in input file")
    
    # Prepare data
    data = {
        "instruction": df[args.instruction_column].tolist(),
        "output": df[args.output_column].tolist(),
    }
    
    # Handle input column if it exists
    if args.input_column in df.columns:
        data["input"] = df[args.input_column].tolist()
    else:
        data["input"] = [""] * len(df)
    
    # Create dataset
    dataset = Dataset.from_dict(data)
    
    # Split dataset if needed
    if args.create_validation:
        dataset = dataset.train_test_split(test_size=args.split_ratio, seed=42)
        train_dataset = dataset["train"]
        val_dataset = dataset["test"]
        
        # Save training data
        train_output_file = args.output_file
        train_dataset.to_json(train_output_file)
        print(f"Training data saved to {train_output_file} ({len(train_dataset)} examples)")
        
        # Save validation data
        val_output_file = os.path.splitext(args.output_file)[0] + "_validation.jsonl"
        val_dataset.to_json(val_output_file)
        print(f"Validation data saved to {val_output_file} ({len(val_dataset)} examples)")
    else:
        # Save all data
        dataset.to_json(args.output_file)
        print(f"Data saved to {args.output_file} ({len(dataset)} examples)")
    
    # Print sample
    print("\nSample formatted example:")
    sample_idx = 0
    sample = {
        "instruction": data["instruction"][sample_idx],
        "input": data["input"][sample_idx],
        "output": data["output"][sample_idx]
    }
    print(format_instruction(sample))

if __name__ == "__main__":
    main()
