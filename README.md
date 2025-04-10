# Scripts Directory

This directory contains scripts for training and using the Octavia Voice model.

## Files

- `train.py` - Main training script for fine-tuning the model with LoRA
- `merge_lora.py` - Script to merge LoRA weights into the base model
- `inference.py` - Script for generating text with the fine-tuned model
- `evaluate.py` - Script for evaluating model performance
- `prepare_dataset.py` - Script for processing and formatting training data

## Usage

### Training

To train the model:

```bash
python scripts/train.py \
  --base_model mistralai/Mistral-7B-Instruct-v0.2 \
  --data_path data/octavia_voice_examples.jsonl \
  --output_dir models/adapter_model \
  --config_path configs/training_config.json
```

### Inference

To generate text with the model:

```bash
python scripts/inference.py \
  --base_model mistralai/Mistral-7B-Instruct-v0.2 \
  --adapter_model models/adapter_model \
  --prompt "Write a fashion review for Luxe Queer magazine" \
  --config_path configs/generation_config.json
```

### Evaluation

To evaluate the model:

```bash
python scripts/evaluate.py \
  --base_model mistralai/Mistral-7B-Instruct-v0.2 \
  --adapter_model models/adapter_model \
  --eval_data data/octavia_voice_validation.jsonl \
  --output_dir evaluation_results
```

## Requirements

See `requirements.txt` in the root directory for dependencies.
