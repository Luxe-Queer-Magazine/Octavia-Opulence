# Octavia Voice Fine-Tuning Approach for Mistral and Gemma Models

## Overview

This document outlines a comprehensive approach for fine-tuning both Mistral and Gemma models to create the Octavia Voice for Luxe Queer magazine's AI Social Media Manager. By leveraging the strengths of both models, we can create a sophisticated system that captures Octavia's distinctive voice across different content types.

## Model Selection

### Primary Models

1. **Mistral-7B-Instruct-v0.2**
   - Size: 7 billion parameters
   - Strengths: Creative text generation, instruction following
   - Use case: Social media content, Blue Lipstick Edit, audience engagement

2. **Gemma-7B-It**
   - Size: 7 billion parameters
   - Strengths: Reasoning, factual content, responsible AI
   - Use case: Luxury descriptions, trend analysis, editorial content

### Scaling Options (Future)

1. **Mistral-Small-3.1-24B-Instruct**
   - Size: 24 billion parameters
   - Advantages: Enhanced capabilities, more nuanced understanding
   - When to use: After successful implementation of 7B model

2. **Gemma-27B-It**
   - Size: 27 billion parameters
   - Advantages: Deeper reasoning, more sophisticated outputs
   - When to use: For premium content requiring highest quality

## Fine-Tuning Approach

### Parameter-Efficient Fine-Tuning

1. **LoRA (Low-Rank Adaptation)**
   - Method: Fine-tune adapter layers while freezing base model
   - Advantages: Efficient training, smaller storage requirements
   - Configuration:
     - Rank: 16
     - Alpha: 32
     - Dropout: 0.05
     - Target modules: q_proj, v_proj, k_proj, o_proj, gate_proj, up_proj, down_proj

2. **QLoRA**
   - Method: Quantized LoRA for larger models
   - Advantages: Enables fine-tuning larger models on consumer hardware
   - When to use: For 24B/27B models or limited GPU resources

### Training Data Preparation

1. **Data Categories**
   - Octavia voice examples (50-100 high-quality samples)
   - Luxury content examples (200-300 samples)
   - Queer cultural content (200-300 samples)
   - Response examples (100-150 samples)

2. **Data Format**
   ```json
   {
     "prompt": "Write a social media post about the latest fashion week in Octavia's voice:",
     "completion": "Darlings, let me be crystalline about this—what we witnessed on the runways this week wasn't just clothing, it was revolution draped in luxury. The boundaries between gendered fashion didn't just blur, they evaporated in a cloud of exquisite tailoring and unapologetic expression. Take notes, because this isn't just next season's look—it's the future refusing to ask permission. #BlueLipstickEdit #LuxeQueer"
   }
   ```

3. **Prompt Templates**
   - Mistral template:
     ```
     <s>[INST] {prompt} [/INST]
     ```
   - Gemma template:
     ```
     <start_of_turn>user
     {prompt}<end_of_turn>
     <start_of_turn>model
     ```

### Training Process

1. **Initial Fine-Tuning**
   - Epochs: 3-5
   - Learning rate: 2e-4 with cosine scheduler
   - Batch size: 4-8 depending on GPU memory
   - Gradient accumulation: 4-8 steps
   - Weight decay: 0.01
   - Warmup steps: 100

2. **Evaluation**
   - Perplexity on held-out examples
   - ROUGE and BLEU scores against reference outputs
   - Human evaluation of voice consistency
   - Brand alignment assessment

3. **Iterative Refinement**
   - Add examples based on evaluation results
   - Adjust hyperparameters as needed
   - Fine-tune specific aspects (tone, style, vocabulary)

## Implementation Code

### Setup Environment

```python
# requirements.txt
transformers>=4.34.0
peft>=0.5.0
accelerate>=0.21.0
bitsandbytes>=0.40.0
torch>=2.0.0
datasets>=2.14.0
trl>=0.7.1
```

### Fine-Tuning Script for Mistral

```python
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Configuration
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
OUTPUT_DIR = "octavia-voice-mistral"
DATASET_PATH = "luxe-queer/octavia-voice-examples"

# Load model with quantization for efficiency
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model = prepare_model_for_kbit_training(model)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj", "v_proj", "k_proj", "o_proj", 
        "gate_proj", "up_proj", "down_proj"
    ]
)
model = get_peft_model(model, lora_config)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Load and prepare dataset
def format_mistral_prompt(example):
    return {
        "text": f"<s>[INST] {example['prompt']} [/INST] {example['completion']}</s>"
    }

dataset = load_dataset(DATASET_PATH)
tokenized_dataset = dataset.map(
    lambda examples: tokenizer(
        [format_mistral_prompt(example) for example in examples], 
        truncation=True, 
        max_length=2048
    ),
    batched=True,
    remove_columns=["prompt", "completion"]
)

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_steps=100,
    max_steps=1000,
    fp16=True,
    logging_steps=10,
    save_steps=200,
    weight_decay=0.01,
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Start training
trainer.train()

# Save the model
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
```

### Fine-Tuning Script for Gemma

```python
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Configuration
MODEL_NAME = "google/gemma-7b-it"
OUTPUT_DIR = "octavia-voice-gemma"
DATASET_PATH = "luxe-queer/octavia-voice-examples"

# Load model with quantization for efficiency
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model = prepare_model_for_kbit_training(model)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj", "v_proj", "k_proj", "o_proj", 
        "gate_proj", "up_proj", "down_proj"
    ]
)
model = get_peft_model(model, lora_config)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Load and prepare dataset
def format_gemma_prompt(example):
    return {
        "text": f"<start_of_turn>user\n{example['prompt']}<end_of_turn>\n<start_of_turn>model\n{example['completion']}<end_of_turn>"
    }

dataset = load_dataset(DATASET_PATH)
tokenized_dataset = dataset.map(
    lambda examples: tokenizer(
        [format_gemma_prompt(example) for example in examples], 
        truncation=True, 
        max_length=2048
    ),
    batched=True,
    remove_columns=["prompt", "completion"]
)

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_steps=100,
    max_steps=1000,
    fp16=True,
    logging_steps=10,
    save_steps=200,
    weight_decay=0.01,
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Start training
trainer.train()

# Save the model
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
```

## Demo Space Implementation

### Gradio Interface

```python
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftModel

# Load Mistral model
def load_mistral_model():
    base_model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.2",
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, "LuxeQueer/octavia-voice-mistral")
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
    return model, tokenizer

# Load Gemma model
def load_gemma_model():
    base_model = AutoModelForCausalLM.from_pretrained(
        "google/gemma-7b-it",
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, "LuxeQueer/octavia-voice-gemma")
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-7b-it")
    return model, tokenizer

# Generate text with Mistral
def generate_with_mistral(prompt, max_length=500, temperature=0.7):
    model, tokenizer = load_mistral_model()
    formatted_prompt = f"<s>[INST] {prompt} [/INST]"
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        temperature=temperature,
        top_p=0.9,
        do_sample=True,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract just the response part
    response = response.split("[/INST]")[-1].strip()
    return response

# Generate text with Gemma
def generate_with_gemma(prompt, max_length=500, temperature=0.7):
    model, tokenizer = load_gemma_model()
    formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        temperature=temperature,
        top_p=0.9,
        do_sample=True,
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract just the response part
    response = response.split("<start_of_turn>model")[-1].strip()
    if "<end_of_turn>" in response:
        response = response.split("<end_of_turn>")[0].strip()
    return response

# Generate with selected model
def generate(prompt, model_choice, max_length, temperature):
    if model_choice == "Mistral":
        return generate_with_mistral(prompt, max_length, temperature)
    else:
        return generate_with_gemma(prompt, max_length, temperature)

# Create Gradio interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown(
        """
        # Octavia Opulence³ Voice Generator
        
        Generate content in the distinctive voice of Octavia Opulence³, the editorial persona of Luxe Queer magazine.
        
        ![Blue Lipstick](https://huggingface.co/datasets/luxe-queer/brand-assets/resolve/main/blue_lipstick_icon.png)
        """
    )
    
    with gr.Row():
        with gr.Column():
            model_choice = gr.Radio(
                ["Mistral", "Gemma"], 
                label="Select Model", 
                value="Mistral",
                info="Mistral excels at creative content, Gemma at factual content"
            )
            
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="Write a social media post about sustainable luxury fashion in Octavia's voice:",
                lines=4
            )
            
            with gr.Accordion("Advanced Options", open=False):
                max_length = gr.Slider(
                    minimum=100, maximum=1000, value=500, step=50,
                    label="Maximum Length"
                )
                temperature = gr.Slider(
                    minimum=0.1, maximum=1.0, value=0.7, step=0.1,
                    label="Temperature (Creativity)"
                )
            
            generate_btn = gr.Button("Generate in Octavia's Voice")
        
        with gr.Column():
            output = gr.Textbox(
                label="Octavia Says:",
                lines=12
            )
    
    with gr.Accordion("Example Prompts", open=True):
        gr.Examples(
            [
                ["Write a social media post about the latest fashion week in Octavia's voice:"],
                ["Create a Blue Lipstick Edit commentary on luxury hotel design in Octavia's voice:"],
                ["Write a response to a comment asking about the definition of queer luxury in Octavia's voice:"],
                ["Draft an editor's letter about the intersection of technology and luxury fashion in Octavia's voice:"],
                ["Create an Instagram caption for a blue lipstick editorial photoshoot in Octavia's voice:"]
            ],
            inputs=prompt
        )
    
    generate_btn.click(
        generate,
        inputs=[prompt, model_choice, max_length, temperature],
        outputs=output
    )
    
    gr.Markdown(
        """
        ## About Octavia Opulence³
        
        Octavia embodies Luxe Queer magazine's unique position at the intersection of luxury and queer identity. Her voice is:
        - Sophisticated yet accessible
        - Authoritative but playful
        - Unapologetically queer
        - Discerning with purpose
        - Culturally fluent
        
        Learn more about [Luxe Queer Magazine](https://huggingface.co/LuxeQueer)
        """
    )

demo.launch()
```

## Ensemble Approach (Advanced Implementation)

For a more sophisticated implementation, we can create an ensemble system that leverages both models:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

class OctaviaVoiceEnsemble:
    def __init__(self):
        # Load Mistral model
        self.mistral_base = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.2",
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        self.mistral_model = PeftModel.from_pretrained(
            self.mistral_base, 
            "LuxeQueer/octavia-voice-mistral"
        )
        self.mistral_tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.2"
        )
        
        # Load Gemma model
        self.gemma_base = AutoModelForCausalLM.from_pretrained(
            "google/gemma-7b-it",
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        self.gemma_model = PeftModel.from_pretrained(
            self.gemma_base, 
            "LuxeQueer/octavia-voice-gemma"
        )
        self.gemma_tokenizer = AutoTokenizer.from_pretrained(
            "google/gemma-7b-it"
        )
        
        # Content type classifier
        self.content_types = {
            "social_media": "mistral",
            "blue_lipstick_edit": "mistral",
            "editorial": "gemma",
            "luxury_description": "gemma",
            "audience_engagement": "mistral"
        }
    
    def classify_content_type(self, prompt):
        # Simple keyword-based classification
        # In production, use a proper classifier
        prompt_lower = prompt.lower()
        
        if any(term in prompt_lower for term in ["social media", "instagram", "twitter", "facebook"]):
            return "social_media"
        elif any(term in prompt_lower for term in ["blue lipstick", "commentary", "critique"]):
            return "blue_lipstick_edit"
        elif any(term in prompt_lower for term in ["editorial", "article", "feature"]):
            return "editorial"
        elif any(term in prompt_lower for term in ["describe", "product", "collection"]):
            return "luxury_description"
        elif any(term in prompt_lower for term in ["response", "reply", "comment", "message"]):
            return "audience_engagement"
        else:
            # Default to mistral for general content
            return "social_media"
    
    def generate(self, prompt, max_length=500, temperature=0.7):
        # Determine content type and select model
        content_type = self.classify_content_type(prompt)
        model_choice = self.content_types.get(content_type, "mistral")
        
        if model_choice == "mistral":
            return self.generate_with_mistral(prompt, max_length, temperature)
        else:
            return self.generate_with_gemma(prompt, max_length, temperature)
    
    def generate_with_mistral(self, prompt, max_length, temperature):
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        inputs = self.mistral_tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
        
        outputs = self.mistral_model.generate(
            **inputs,
            max_length=max_length,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
        )
        
        response = self.mistral_tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.split("[/INST]")[-1].strip()
        return response
    
    def generate_with_gemma(self, prompt, max_length, temperature):
        formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
        inputs = self.gemma_tokenizer(formatted_prompt, return_tensors="pt").to("cuda")
        
        outputs = self.gemma_model.generate(
            **inputs,
            max_length=max_length,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
        )
        
        response = self.gemma_tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.split("<start_of_turn>model")[-1].strip()
        if "<end_of_turn>" in response:
            response = response.split("<end_of_turn>")[0].strip()
        return response
```

## Next Steps

1. **Create Training Dataset**
   - Collect examples of Octavia's voice from existing content
   - Create additional examples based on brand guidelines
   - Format data according to model requirements

2. **Set Up Training Environment**
   - Configure GPU instance with appropriate memory
   - Install required libraries and dependencies
   - Prepare training scripts

3. **Fine-Tune Models**
   - Start with smaller 7B models
   - Implement LoRA fine-tuning
   - Evaluate and refine

4. **Create Demo Space**
   - Implement Gradio interface
   - Add Luxe Queer branding
   - Configure model selection

5. **Integrate with Meta API**
   - Develop middleware for API access
   - Implement content generation pipeline
   - Set up monitoring and evaluation

This fine-tuning approach provides a comprehensive strategy for developing Octavia's voice using both Mistral and Gemma models, leveraging their respective strengths to create a sophisticated AI system for Luxe Queer magazine's social media presence.
