# Visual Guide: Setting Up Octavia Voice on Hugging Face

This step-by-step visual guide will walk you through the process of setting up the Octavia Voice model on Hugging Face. Each section includes clear instructions with explanations of what you're doing and why.

## Table of Contents
1. [Creating Your Hugging Face Account](#1-creating-your-hugging-face-account)
2. [Setting Up Your Organization](#2-setting-up-your-organization)
3. [Creating the Octavia Voice Repository](#3-creating-the-octavia-voice-repository)
4. [Uploading Repository Files](#4-uploading-repository-files)
5. [Setting Up the Model Card](#5-setting-up-the-model-card)
6. [Training the Model](#6-training-the-model)
7. [Creating a Demo Space](#7-creating-a-demo-space)
8. [Troubleshooting](#8-troubleshooting)

## 1. Creating Your Hugging Face Account

**Step 1:** Visit [huggingface.co](https://huggingface.co) and click "Sign Up" in the top right corner.

![Hugging Face Sign Up](https://i.imgur.com/example1.png)
*The Hugging Face homepage with the Sign Up button highlighted*

**Step 2:** Fill in your details to create an account.
- Use a business email if possible
- Create a strong password
- Accept the terms of service

**Step 3:** Verify your email address by clicking the link sent to your inbox.

**Step 4:** Complete your profile with a professional photo and bio that mentions Luxe Queer magazine.

## 2. Setting Up Your Organization

**Step 1:** Click on your profile picture in the top right corner and select "New Organization".

![Create Organization](https://i.imgur.com/example2.png)
*The dropdown menu with "New Organization" highlighted*

**Step 2:** Enter "LuxeQueer" as the organization name.
- This will create the URL: huggingface.co/LuxeQueer

**Step 3:** Add a profile picture (ideally your logo with the blue lipstick element).

**Step 4:** Add a description for your organization. You can copy this from the organization card we created earlier.

**Step 5:** Set the organization to "Private" initially (you can make it public later).

## 3. Creating the Octavia Voice Repository

**Step 1:** From your organization page, click the "New" button and select "Model".

![New Model](https://i.imgur.com/example3.png)
*The organization page with the "New" button highlighted*

**Step 2:** Name your repository "Octavia-Voice".
- This will create the URL: huggingface.co/LuxeQueer/Octavia-Voice

**Step 3:** Set the repository to "Private" initially.

**Step 4:** Choose "Empty Repository" as the template.

**Step 5:** Click "Create repository".

## 4. Uploading Repository Files

**Step 1:** You'll see your empty repository. Click on "Add file" and select "Upload files".

![Upload Files](https://i.imgur.com/example4.png)
*The repository page with "Add file" dropdown highlighted*

**Step 2:** Extract the ZIP file I provided (octavia_voice_repo.zip) to your local computer.

**Step 3:** Upload the files in this order (you'll need to do multiple uploads):

1. First upload:
   - README.md
   - IMPLEMENTATION_GUIDE.md

2. Second upload:
   - configs/config.json
   - configs/generation_config.json
   - configs/tokenizer_config.json
   - configs/training_config.json
   - configs/README.md

3. Third upload:
   - data/octavia_style_guide.md
   - data/octavia_voice_examples.jsonl
   - data/octavia_voice_validation.jsonl
   - data/README.md

4. Fourth upload:
   - models/README.md
   - scripts/README.md

5. Final upload:
   - scripts/train.py
   - scripts/merge_lora.py
   - scripts/inference.py
   - scripts/evaluate.py
   - scripts/prepare_dataset.py

**Step 4:** After each upload, add a commit message like "Add README files" or "Add configuration files" and click "Commit changes".

## 5. Setting Up the Model Card

**Step 1:** Your README.md file will automatically become your model card, but you need to set up the metadata. Click on "Metadata UI" at the top of your repository.

![Metadata UI](https://i.imgur.com/example5.png)
*The repository page with "Metadata UI" tab highlighted*

**Step 2:** Fill in the metadata fields:

- **License**: Select "Apache License 2.0"
- **Datasets**: Add "fka/awesome-chatgpt-prompts" and any other datasets you want to reference
- **Language**: Select "English"
- **Base Model**: Add "mistralai/Mistral-7B-Instruct-v0.2" (or your preferred base model)
- **Pipeline Tag**: Select "Text Generation"
- **Tags**: Add "octavia", "luxe-queer", "editorial", "luxury"
- **Metrics**: Add "bertscore" and any other metrics you want to track
- **Library Name**: Add "transformers"

**Step 3:** Click "Save" to update your model card metadata.

## 6. Training the Model

There are two approaches to training the model:

### Option A: Using Hugging Face AutoTrain (Easiest)

**Step 1:** Go to [autotrain.huggingface.co](https://autotrain.huggingface.co) and log in with your Hugging Face account.

**Step 2:** Click "New Project" and select "Text Generation".

**Step 3:** Upload your training data (data/octavia_voice_examples.jsonl) and validation data (data/octavia_voice_validation.jsonl).

**Step 4:** Select "mistralai/Mistral-7B-Instruct-v0.2" as your base model.

**Step 5:** Configure training parameters:
- Training type: LoRA
- LoRA rank: 16
- LoRA alpha: 32
- Learning rate: 2e-5
- Number of epochs: 3

**Step 6:** Start training and wait for completion (this may take several hours).

### Option B: Using Your Own Hardware (More Control)

If you have access to a GPU machine:

**Step 1:** Clone your repository:
```bash
git lfs install
git clone https://huggingface.co/LuxeQueer/Octavia-Voice
cd Octavia-Voice
```

**Step 2:** Install required packages:
```bash
pip install -r requirements.txt
```

**Step 3:** Run the training script:
```bash
python scripts/train.py \
  --base_model mistralai/Mistral-7B-Instruct-v0.2 \
  --data_path data/octavia_voice_examples.jsonl \
  --eval_data_path data/octavia_voice_validation.jsonl \
  --output_dir models/adapter_model \
  --config_path configs/training_config.json
```

**Step 4:** Push the trained model back to Hugging Face:
```bash
git add models/adapter_model
git commit -m "Add trained model"
git push
```

## 7. Creating a Demo Space

**Step 1:** From your Hugging Face profile, click "New Space".

![New Space](https://i.imgur.com/example6.png)
*The profile page with "New Space" button highlighted*

**Step 2:** Name your space "Octavia-Voice-Demo".

**Step 3:** Select "Gradio" as the SDK.

**Step 4:** Set the space to "Public" so others can try your model.

**Step 5:** Create the space and you'll be taken to the code editor.

**Step 6:** Replace the default app.py with this code:

```python
import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from peft import PeftModel

# Load model and tokenizer
base_model = "mistralai/Mistral-7B-Instruct-v0.2"
adapter_model = "LuxeQueer/Octavia-Voice"

tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype=torch.float16,
    device_map="auto"
)
model = PeftModel.from_pretrained(model, adapter_model)

def format_prompt(instruction, input_text=None):
    if input_text:
        return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
    else:
        return f"### Instruction:\n{instruction}\n\n### Response:\n"

def generate(instruction, input_text="", temperature=0.7, max_length=1024):
    prompt = format_prompt(instruction, input_text if input_text else None)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    generation_config = GenerationConfig(
        temperature=temperature,
        top_p=0.9,
        top_k=50,
        max_new_tokens=max_length,
        repetition_penalty=1.1,
    )
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            generation_config=generation_config,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(prompt):]

# Create Gradio interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# Octavia Voice - Luxe Queer Magazine")
    gr.Markdown("Generate content in the distinctive voice of Octavia Opulence³, the editorial persona of Luxe Queer magazine.")
    
    with gr.Row():
        with gr.Column():
            instruction = gr.Textbox(label="Instruction", placeholder="Write a fashion review for Luxe Queer magazine")
            input_text = gr.Textbox(label="Input (Optional)", placeholder="Review the latest collection from Prada...")
            temperature = gr.Slider(minimum=0.1, maximum=1.5, value=0.7, step=0.1, label="Temperature")
            max_length = gr.Slider(minimum=64, maximum=4096, value=1024, step=64, label="Maximum Length")
            submit_btn = gr.Button("Generate")
        
        with gr.Column():
            output = gr.Textbox(label="Octavia's Response", lines=20)
    
    submit_btn.click(
        generate,
        inputs=[instruction, input_text, temperature, max_length],
        outputs=output
    )
    
    gr.Markdown("## Example Instructions")
    gr.Markdown("""
    - Write an editor's letter for the summer issue of Luxe Queer magazine
    - Write a review of a luxury hotel in Paris that claims to be LGBTQ+ friendly
    - Write a response to a reader's letter about breaking into the luxury fashion industry
    - Write a piece for The Blue Lipstick Edit about luxury brands' Pride campaigns
    """)

demo.launch()
```

**Step 7:** Create a requirements.txt file with these dependencies:
```
gradio>=3.50.2
torch>=2.0.0
transformers>=4.38.0
peft>=0.7.0
accelerate>=0.25.0
```

**Step 8:** Click "Save" and wait for your Space to build and deploy.

## 8. Troubleshooting

### Common Issues and Solutions

**Issue 1: Upload Errors**
- **Solution**: Try uploading fewer files at once, or use Git instead of the web interface

**Issue 2: Training Out of Memory**
- **Solution**: Reduce batch size in training_config.json or use a smaller base model

**Issue 3: Model Not Generating Good Content**
- **Solution**: Add more diverse training examples or increase training epochs

**Issue 4: Space Fails to Build**
- **Solution**: Check the build logs for errors and ensure all dependencies are listed in requirements.txt

### Getting Help

If you encounter issues not covered here:

1. Check the Hugging Face forums at [discuss.huggingface.co](https://discuss.huggingface.co)
2. Review the documentation at [huggingface.co/docs](https://huggingface.co/docs)
3. Feel free to reach out to me for additional assistance

## Next Steps After Setup

Once your Octavia Voice model is set up and working:

1. **Refine the model** by adding more training examples
2. **Integrate with your website** using the Hugging Face Inference API
3. **Connect to your social media** using the middleware approach described in the implementation guide
4. **Create specialized versions** for different content types (fashion, travel, etc.)

Remember that this is an iterative process. Start with a basic implementation, test it thoroughly, and then expand its capabilities based on your specific needs for Luxe Queer magazine.

---

This visual guide provides a comprehensive walkthrough for setting up the Octavia Voice model on Hugging Face. By following these steps, you'll create a sophisticated AI system that embodies the distinctive voice of Octavia Opulence³ for your Luxe Queer magazine.
