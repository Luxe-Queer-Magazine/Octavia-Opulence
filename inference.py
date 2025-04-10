#!/usr/bin/env python
# coding=utf-8

import os
import json
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from peft import PeftModel

def format_prompt(instruction, input_text=None):
    """Format the instruction and input into a prompt."""
    if input_text:
        return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
    else:
        return f"### Instruction:\n{instruction}\n\n### Response:\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, required=True, help="Base model path")
    parser.add_argument("--adapter_model", type=str, default=None, help="LoRA adapter model path (if not merged)")
    parser.add_argument("--prompt", type=str, required=True, help="Instruction prompt")
    parser.add_argument("--input", type=str, default=None, help="Optional input text")
    parser.add_argument("--config_path", type=str, default=None, help="Path to generation config")
    parser.add_argument("--max_new_tokens", type=int, default=1024, help="Maximum number of new tokens")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for sampling")
    parser.add_argument("--top_p", type=float, default=0.9, help="Top-p sampling parameter")
    parser.add_argument("--top_k", type=int, default=50, help="Top-k sampling parameter")
    parser.add_argument("--repetition_penalty", type=float, default=1.1, help="Repetition penalty")
    args = parser.parse_args()
    
    # Load tokenizer
    print(f"Loading tokenizer from {args.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    
    # Load model
    print(f"Loading model from {args.base_model}")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    
    # Load adapter if specified
    if args.adapter_model:
        print(f"Loading adapter from {args.adapter_model}")
        model = PeftModel.from_pretrained(model, args.adapter_model)
    
    # Load generation config if specified
    if args.config_path:
        print(f"Loading generation config from {args.config_path}")
        with open(args.config_path, 'r') as f:
            gen_config_dict = json.load(f)
        generation_config = GenerationConfig(**gen_config_dict)
    else:
        # Use command line arguments for generation config
        generation_config = GenerationConfig(
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            top_k=args.top_k,
            repetition_penalty=args.repetition_penalty,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id,
        )
    
    # Format prompt
    prompt = format_prompt(args.prompt, args.input)
    print("\n===== PROMPT =====")
    print(prompt)
    print("==================\n")
    
    # Tokenize prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate response
    print("Generating response...")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            generation_config=generation_config,
        )
    
    # Decode and print response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the response part (after the prompt)
    response = response[len(prompt):]
    
    print("\n===== RESPONSE =====")
    print(response)
    print("====================\n")

if __name__ == "__main__":
    main()
