#!/usr/bin/env python
# coding=utf-8

import os
import json
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, required=True, help="Base model to merge with adapter")
    parser.add_argument("--adapter_model", type=str, required=True, help="LoRA adapter model to merge")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for merged model")
    parser.add_argument("--half", action="store_true", help="Save model in half precision")
    args = parser.parse_args()
    
    print(f"Loading base model: {args.base_model}")
    base_model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.float16 if args.half else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )
    
    print(f"Loading adapter model: {args.adapter_model}")
    model = PeftModel.from_pretrained(base_model, args.adapter_model)
    
    print("Merging adapter weights into base model...")
    model = model.merge_and_unload()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Saving merged model to {args.output_dir}")
    model.save_pretrained(args.output_dir)
    
    # Save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    tokenizer.save_pretrained(args.output_dir)
    
    print("Model merging complete!")

if __name__ == "__main__":
    main()
