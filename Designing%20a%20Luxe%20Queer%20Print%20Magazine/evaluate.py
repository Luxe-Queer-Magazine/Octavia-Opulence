#!/usr/bin/env python
# coding=utf-8

import os
import json
import argparse
import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from datasets import load_dataset
from evaluate import load
from rouge_score import rouge_scorer

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
    parser.add_argument("--eval_data", type=str, required=True, help="Path to evaluation data")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for evaluation results")
    parser.add_argument("--max_new_tokens", type=int, default=1024, help="Maximum number of new tokens")
    parser.add_argument("--batch_size", type=int, default=1, help="Batch size for evaluation")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
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
    
    # Load evaluation data
    print(f"Loading evaluation data from {args.eval_data}")
    eval_dataset = load_dataset("json", data_files=args.eval_data)["train"]
    
    # Load evaluation metrics
    bertscore = load("bertscore")
    rouge_scorer_instance = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # Prepare results storage
    results = {
        "samples": [],
        "metrics": {
            "bertscore": {"precision": [], "recall": [], "f1": []},
            "rouge1": {"precision": [], "recall": [], "f1": []},
            "rouge2": {"precision": [], "recall": [], "f1": []},
            "rougeL": {"precision": [], "recall": [], "f1": []},
        }
    }
    
    # Evaluate model
    print("Starting evaluation...")
    model.eval()
    
    for i, example in enumerate(tqdm(eval_dataset)):
        # Format prompt
        prompt = format_prompt(example["instruction"], example["input"])
        
        # Tokenize prompt
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,  # Use greedy decoding for evaluation
            )
        
        # Decode and extract response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_response = full_response[len(prompt):]
        
        # Calculate metrics
        # BERTScore
        bert_results = bertscore.compute(
            predictions=[generated_response], 
            references=[example["output"]], 
            lang="en"
        )
        
        # ROUGE
        rouge_results = rouge_scorer_instance.score(example["output"], generated_response)
        
        # Store results
        sample_result = {
            "id": i,
            "instruction": example["instruction"],
            "input": example["input"],
            "reference": example["output"],
            "generated": generated_response,
            "metrics": {
                "bertscore": {
                    "precision": bert_results["precision"][0],
                    "recall": bert_results["recall"][0],
                    "f1": bert_results["f1"][0]
                },
                "rouge1": {
                    "precision": rouge_results["rouge1"].precision,
                    "recall": rouge_results["rouge1"].recall,
                    "f1": rouge_results["rouge1"].fmeasure
                },
                "rouge2": {
                    "precision": rouge_results["rouge2"].precision,
                    "recall": rouge_results["rouge2"].recall,
                    "f1": rouge_results["rouge2"].fmeasure
                },
                "rougeL": {
                    "precision": rouge_results["rougeL"].precision,
                    "recall": rouge_results["rougeL"].recall,
                    "f1": rouge_results["rougeL"].fmeasure
                }
            }
        }
        
        results["samples"].append(sample_result)
        
        # Accumulate metrics
        results["metrics"]["bertscore"]["precision"].append(bert_results["precision"][0])
        results["metrics"]["bertscore"]["recall"].append(bert_results["recall"][0])
        results["metrics"]["bertscore"]["f1"].append(bert_results["f1"][0])
        
        results["metrics"]["rouge1"]["precision"].append(rouge_results["rouge1"].precision)
        results["metrics"]["rouge1"]["recall"].append(rouge_results["rouge1"].recall)
        results["metrics"]["rouge1"]["f1"].append(rouge_results["rouge1"].fmeasure)
        
        results["metrics"]["rouge2"]["precision"].append(rouge_results["rouge2"].precision)
        results["metrics"]["rouge2"]["recall"].append(rouge_results["rouge2"].recall)
        results["metrics"]["rouge2"]["f1"].append(rouge_results["rouge2"].fmeasure)
        
        results["metrics"]["rougeL"]["precision"].append(rouge_results["rougeL"].precision)
        results["metrics"]["rougeL"]["recall"].append(rouge_results["rougeL"].recall)
        results["metrics"]["rougeL"]["f1"].append(rouge_results["rougeL"].fmeasure)
    
    # Calculate average metrics
    for metric in results["metrics"]:
        for key in results["metrics"][metric]:
            results["metrics"][metric][f"avg_{key}"] = float(np.mean(results["metrics"][metric][key]))
    
    # Save results
    results_path = os.path.join(args.output_dir, "evaluation_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n===== EVALUATION SUMMARY =====")
    print(f"Total samples evaluated: {len(eval_dataset)}")
    print("\nAverage metrics:")
    print(f"BERTScore F1: {results['metrics']['bertscore']['avg_f1']:.4f}")
    print(f"ROUGE-1 F1: {results['metrics']['rouge1']['avg_f1']:.4f}")
    print(f"ROUGE-2 F1: {results['metrics']['rouge2']['avg_f1']:.4f}")
    print(f"ROUGE-L F1: {results['metrics']['rougeL']['avg_f1']:.4f}")
    print(f"\nDetailed results saved to {results_path}")

if __name__ == "__main__":
    main()
