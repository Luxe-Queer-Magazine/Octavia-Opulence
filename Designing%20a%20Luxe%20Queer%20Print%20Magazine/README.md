# Octavia Voice Training Data

This directory contains the training data for fine-tuning the Octavia Opulence³ voice model. The data is structured in the format required by Hugging Face's training pipeline.

## Data Format

The training data is provided in JSONL format, with each line containing a JSON object with the following structure:

```json
{
  "instruction": "The prompt or instruction given to the model",
  "input": "Optional additional context or input",
  "output": "The expected response in Octavia's voice"
}
```

## Data Files

- `octavia_voice_examples.jsonl`: Main training dataset with examples of Octavia's voice
- `octavia_voice_validation.jsonl`: Validation dataset for evaluating model performance
- `octavia_style_guide.md`: Detailed guide on Octavia's voice characteristics and style

## Usage

These files should be used with the training scripts in the `scripts` directory to fine-tune the selected base models (Mistral and Gemma).
