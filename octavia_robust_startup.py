#!/usr/bin/env python3
"""
Robust Startup Script for Octavia Opulence³ Digital Human Implementation
in Hugging Face Space Environment

This script handles proper path resolution, comprehensive error checking,
and all necessary setup steps for the Octavia digital human implementation.
"""

import os
import sys
import subprocess
import time
import argparse
import platform
import json
from pathlib import Path

# ANSI color codes for prettier output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configuration
CONFIG = {
    "log_file": "octavia_setup.log",
    "conda_packages": [
        "pytorch torchvision torchaudio -c pytorch",
        "cudatoolkit=11.8 -c pytorch -c nvidia",
    ],
    "pip_packages": [
        "transformers==4.30.2",
        "datasets==2.14.5",
        "accelerate==0.21.0",
        "opencv-python==4.8.0.76",
        "mediapipe==0.10.3",
        "huggingface_hub==0.16.4",
        "numpy==1.24.3",
        "pillow==10.0.0",
        "scikit-image==0.21.0",
        "matplotlib==3.7.2",
        "tqdm==4.66.1"
    ],
    "directories": [
        "octavia_data",
        "octavia_models",
        "octavia_output"
    ]
}

class OctaviaSetup:
    def __init__(self, args):
        self.args = args
        self.start_time = time.time()
        self.log_file = CONFIG["log_file"]
        self.base_dir = self._get_base_dir()
        self.env_info = self._get_environment_info()
        
        # Create log file
        with open(self.log_file, "w") as f:
            f.write(f"Octavia Opulence³ Setup Log - {time.ctime()}\n")
            f.write(f"Environment: {json.dumps(self.env_info, indent=2)}\n\n")
        
        self.log(f"{Colors.HEADER}{Colors.BOLD}Octavia Opulence³ Digital Human Setup{Colors.ENDC}")
        self.log(f"Base directory: {self.base_dir}")
        self.log(f"Environment: {platform.system()} {platform.release()}")
        self.log(f"Python: {sys.version}")
        
    def _get_base_dir(self):
        """Get the base directory for the Octavia implementation"""
        # First try to use the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If we're in Hugging Face Space, use /app
        if os.path.exists("/app"):
            return "/app"
        
        return script_dir
    
    def _get_environment_info(self):
        """Gather information about the environment"""
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "is_huggingface_space": os.path.exists("/app"),
            "has_conda": self._check_command("conda"),
            "has_gpu": self._check_gpu(),
            "path": os.environ.get("PATH", "")
        }
        return info
    
    def _check_command(self, command):
        """Check if a command is available"""
        try:
            subprocess.run(["which", command], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _check_gpu(self):
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            try:
                result = subprocess.run(["nvidia-smi"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return result.returncode == 0
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
    
    def log(self, message):
        """Log a message to both console and log file"""
        print(message)
        with open(self.log_file, "a") as f:
            # Strip ANSI color codes for log file
            clean_message = message
            for color in vars(Colors).values():
                if isinstance(color, str) and color.startswith('\033'):
                    clean_message = clean_message.replace(color, '')
            f.write(f"{clean_message}\n")
    
    def run_command(self, command, description=None, critical=False):
        """Run a shell command with proper error handling"""
        if description:
            self.log(f"{Colors.CYAN}• {description}{Colors.ENDC}")
        
        self.log(f"  Running: {command}")
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output in real-time
            stdout_lines = []
            stderr_lines = []
            
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line == '' and stderr_line == '' and process.poll() is not None:
                    break
                
                if stdout_line:
                    stdout_line = stdout_line.strip()
                    print(f"    {stdout_line}")
                    stdout_lines.append(stdout_line)
                
                if stderr_line:
                    stderr_line = stderr_line.strip()
                    print(f"    {Colors.WARNING}{stderr_line}{Colors.ENDC}")
                    stderr_lines.append(stderr_line)
            
            return_code = process.poll()
            
            # Log complete output to file
            with open(self.log_file, "a") as f:
                f.write(f"Command: {command}\n")
                f.write(f"Return code: {return_code}\n")
                f.write("--- STDOUT ---\n")
                f.write("\n".join(stdout_lines) + "\n")
                f.write("--- STDERR ---\n")
                f.write("\n".join(stderr_lines) + "\n\n")
            
            if return_code != 0:
                error_msg = f"{Colors.FAIL}Error executing command: {command}{Colors.ENDC}"
                self.log(error_msg)
                if critical:
                    self.log(f"{Colors.FAIL}Critical error. Exiting.{Colors.ENDC}")
                    sys.exit(1)
                return False
            
            self.log(f"  {Colors.GREEN}Command completed successfully{Colors.ENDC}")
            return True
            
        except Exception as e:
            error_msg = f"{Colors.FAIL}Exception running command: {str(e)}{Colors.ENDC}"
            self.log(error_msg)
            if critical:
                self.log(f"{Colors.FAIL}Critical error. Exiting.{Colors.ENDC}")
                sys.exit(1)
            return False
    
    def create_directories(self):
        """Create necessary directories for Octavia implementation"""
        self.log(f"{Colors.BLUE}{Colors.BOLD}Creating directories...{Colors.ENDC}")
        
        for directory in CONFIG["directories"]:
            dir_path = os.path.join(self.base_dir, directory)
            self.log(f"  Creating directory: {dir_path}")
            try:
                os.makedirs(dir_path, exist_ok=True)
                self.log(f"  {Colors.GREEN}Directory created: {dir_path}{Colors.ENDC}")
            except Exception as e:
                self.log(f"  {Colors.FAIL}Failed to create directory {dir_path}: {str(e)}{Colors.ENDC}")
    
    def setup_conda_environment(self):
        """Setup conda environment for Octavia"""
        if not self.env_info["has_conda"]:
            self.log(f"{Colors.WARNING}Conda not found. Skipping conda setup.{Colors.ENDC}")
            return False
        
        self.log(f"{Colors.BLUE}{Colors.BOLD}Setting up conda environment...{Colors.ENDC}")
        
        # Update conda
        self.run_command("conda update -y conda", "Updating conda")
        
        # Install conda packages
        for package in CONFIG["conda_packages"]:
            self.run_command(f"conda install -y {package}", f"Installing {package} with conda")
        
        return True
    
    def setup_pip_packages(self):
        """Install required pip packages"""
        self.log(f"{Colors.BLUE}{Colors.BOLD}Installing pip packages...{Colors.ENDC}")
        
        # Update pip
        self.run_command("pip install --upgrade pip", "Upgrading pip")
        
        # Install packages
        for package in CONFIG["pip_packages"]:
            self.run_command(f"pip install {package}", f"Installing {package}")
        
        return True
    
    def verify_installation(self):
        """Verify that all required packages are installed correctly"""
        self.log(f"{Colors.BLUE}{Colors.BOLD}Verifying installation...{Colors.ENDC}")
        
        # Check PyTorch with CUDA
        self.run_command(
            "python -c \"import torch; print('PyTorch version:', torch.__version__); "
            "print('CUDA available:', torch.cuda.is_available()); "
            "print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); "
            "print('GPU count:', torch.cuda.device_count() if torch.cuda.is_available() else 0)\"",
            "Checking PyTorch and CUDA"
        )
        
        # Check transformers
        self.run_command(
            "python -c \"import transformers; print('Transformers version:', transformers.__version__)\"",
            "Checking Transformers"
        )
        
        # Check OpenCV
        self.run_command(
            "python -c \"import cv2; print('OpenCV version:', cv2.__version__)\"",
            "Checking OpenCV"
        )
        
        # Check MediaPipe
        self.run_command(
            "python -c \"import mediapipe as mp; print('MediaPipe version:', mp.__version__)\"",
            "Checking MediaPipe"
        )
        
        self.log(f"{Colors.GREEN}{Colors.BOLD}Verification completed{Colors.ENDC}")
        return True
    
    def download_sample_data(self):
        """Download sample data for testing Octavia implementation"""
        if not self.args.download_samples:
            return True
            
        self.log(f"{Colors.BLUE}{Colors.BOLD}Downloading sample data...{Colors.ENDC}")
        
        # Create sample data directory
        sample_dir = os.path.join(self.base_dir, "octavia_data", "samples")
        os.makedirs(sample_dir, exist_ok=True)
        
        # Download sample face image
        self.run_command(
            f"wget -O {sample_dir}/sample_face.jpg https://github.com/opencv/opencv/raw/master/samples/data/lena.jpg",
            "Downloading sample face image"
        )
        
        # Create sample dataset
        sample_dataset = os.path.join(sample_dir, "octavia_sample_dataset.csv")
        with open(sample_dataset, "w") as f:
            f.write("text\n")
            f.write("Darling, luxury isn't what you have—it's how completely you own who you are.\n")
            f.write("In a world of beige conformity, wear blue lipstick and make them remember you.\n")
            f.write("The most exquisite accessory you can wear is your truth.\n")
            f.write("Technology without soul is just machinery. But when innovation meets authentic expression, that's when the future truly becomes luxurious.\n")
            f.write("I've traveled the world, and I can tell you this: true luxury transcends borders, but it never transcends authenticity.\n")
        
        self.log(f"{Colors.GREEN}Sample data downloaded to {sample_dir}{Colors.ENDC}")
        return True
    
    def create_test_script(self):
        """Create a test script to verify Octavia implementation"""
        self.log(f"{Colors.BLUE}{Colors.BOLD}Creating test script...{Colors.ENDC}")
        
        test_script_path = os.path.join(self.base_dir, "test_octavia.py")
        
        with open(test_script_path, "w") as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Test script for Octavia Opulence³ Digital Human Implementation
\"\"\"

import os
import sys
import cv2
import numpy as np
import mediapipe as mp

def test_blue_lipstick():
    \"\"\"Test the blue lipstick facial modeling component\"\"\"
    print("Testing blue lipstick facial modeling...")
    
    # Initialize MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        min_detection_confidence=0.5
    )
    
    # Define lip indices in MediaPipe Face Mesh
    lip_indices = [
        61, 146, 91, 181, 84, 17, 314, 405, 321, 375,
        291, 409, 270, 269, 267, 0, 37, 39, 40, 185
    ]
    
    # Define Octavia's signature blue color
    octavia_blue_bgr = (255, 178, 0)  # BGR format for OpenCV
    
    # Find sample image
    sample_dir = os.path.join("octavia_data", "samples")
    sample_image = os.path.join(sample_dir, "sample_face.jpg")
    
    if not os.path.exists(sample_image):
        print(f"Sample image not found at {sample_image}")
        print("Please run the setup script with --download-samples flag")
        return False
    
    # Read image
    image = cv2.imread(sample_image)
    if image is None:
        print(f"Error: Could not read image {sample_image}")
        return False
    
    # Detect face
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)
    
    if not results.multi_face_landmarks:
        print(f"No face detected in {sample_image}")
        return False
    
    # Create lip mask
    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    
    face_landmarks = results.multi_face_landmarks[0]
    
    # Extract lip points
    lip_points = []
    for idx in lip_indices:
        landmark = face_landmarks.landmark[idx]
        x, y = int(landmark.x * width), int(landmark.y * height)
        lip_points.append([x, y])
    
    # Create polygon from lip points
    lip_points = np.array(lip_points, dtype=np.int32)
    cv2.fillPoly(mask, [lip_points], 255)
    
    # Apply blue lipstick
    lipstick_layer = np.zeros_like(image)
    lipstick_layer[mask > 0] = octavia_blue_bgr
    
    # Blend with original image
    result = cv2.addWeighted(image, 1.0, lipstick_layer, 0.7, 0)
    
    # Add metallic sheen effect
    sheen_mask = np.zeros_like(mask)
    for i in range(height):
        for j in range(width):
            if mask[i, j] > 0:
                gradient_value = int(255 * (j / width))
                sheen_mask[i, j] = gradient_value
    
    sheen_layer = np.zeros_like(image)
    sheen_layer[sheen_mask > 0] = (255, 255, 255)  # White sheen
    
    result = cv2.addWeighted(result, 1.0, sheen_layer, 0.3, 0)
    
    # Save result
    output_dir = os.path.join("octavia_output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "octavia_blue_lipstick_test.jpg")
    cv2.imwrite(output_path, result)
    
    print(f"Blue lipstick test completed successfully")
    print(f"Result saved to {output_path}")
    return True

def test_transformers():
    \"\"\"Test the transformers installation for language model component\"\"\"
    print("Testing transformers installation...")
    
    try:
        from transformers import pipeline
        
        # Create a simple pipeline
        generator = pipeline('text-generation', model='gpt2')
        
        # Generate text
        prompt = "Luxury is"
        result = generator(prompt, max_length=30, num_return_sequences=1)
        
        print("Transformers test completed successfully")
        print(f"Generated text: {result[0]['generated_text']}")
        return True
    except Exception as e:
        print(f"Error testing transformers: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running Octavia Opulence³ implementation tests...")
    
    # Test blue lipstick facial modeling
    blue_lipstick_success = test_blue_lipstick()
    
    # Test transformers for language model
    transformers_success = test_transformers()
    
    # Print summary
    print("\\nTest Summary:")
    print(f"Blue Lipstick Facial Modeling: {'✅ Success' if blue_lipstick_success else '❌ Failed'}")
    print(f"Transformers Language Model: {'✅ Success' if transformers_success else '❌ Failed'}")
    
    if blue_lipstick_success and transformers_success:
        print("\\n✨ All tests passed! Octavia Opulence³ implementation is ready. ✨")
    else:
        print("\\n⚠️ Some tests failed. Please check the output for details.")
""")
        
        # Make the test script executable
        os.chmod(test_script_path, 0o755)
        
        self.log(f"{Colors.GREEN}Test script created at {test_script_path}{Colors.ENDC}")
        self.log(f"  Run with: python {test_script_path}")
        return True
    
    def run(self):
        """Run the complete setup process"""
        self.log(f"{Colors.HEADER}{Colors.BOLD}Starting Octavia Opulence³ setup...{Colors.ENDC}")
        
        # Create directories
        self.create_directories()
        
        # Setup environment
        if self.env_info["has_conda"]:
            self.setup_conda_environment()
        else:
            self.log(f"{Colors.WARNING}Conda not found. Using pip only.{Colors.ENDC}")
        
        # Install pip packages
        self.setup_pip_packages()
        
        # Verify installation
        self.verify_installation()
        
        # Download sample data if requested
        self.download_sample_data()
        
        # Create test script
        self.create_test_script()
        
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(elapsed_time, 60)
        
        # Print completion message
        self.log(f"\n{Colors.GREEN}{Colors.BOLD}Octavia Opulence³ setup completed in {int(minutes)}m {int(seconds)}s!{Colors.ENDC}")
        self.log(f"{Colors.CYAN}Next steps:{Colors.ENDC}")
        self.log(f"  1. Run the test script: {Colors.BOLD}python {os.path.join(self.base_dir, 'test_octavia.py')}{Colors.ENDC}")
        self.log(f"  2. Use the full implementation: {Colors.BOLD}python {os.path.join(self.base_dir, 'octavia_digital_human.py')}{Colors.ENDC}")
        self.log(f"  3. Check the log file for details: {Colors.BOLD}{self.log_file}{Colors.ENDC}")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Octavia Opulence³ Digital Human Setup")
    parser.add_argument("--download-samples", action="store_true", help="Download sample data for testing")
    parser.add_argument("--skip-conda", action="store_true", help="Skip conda setup and use pip only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    setup = OctaviaSetup(args)
    setup.run()


if __name__ == "__main__":
    main()
