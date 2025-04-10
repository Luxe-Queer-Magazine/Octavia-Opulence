import subprocess
import os
import sys

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

# Install required packages correctly
commands = [
    "conda install -y pytorch torchvision torchaudio -c pytorch",
    "pip install transformers datasets accelerate",
    "pip install opencv-python mediapipe numpy",
    "pip install huggingface_hub"
]

for cmd in commands:
    if not run_command(cmd):
        print(f"Failed to run: {cmd}")
        sys.exit(1)

print("Setup completed successfully!")
