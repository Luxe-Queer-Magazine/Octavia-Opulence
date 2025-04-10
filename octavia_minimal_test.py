#!/usr/bin/env python3
"""
Minimal Test Script for Octavia Opulence³ Digital Human Implementation
Avoids dependency issues by using only core Python libraries
"""

import os
import sys
import time
import json

def test_environment():
    """Test the basic Python environment"""
    print("\n===== Testing Python Environment =====")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    
    # Check if we're in a Hugging Face Space
    in_hf_space = os.path.exists("/app")
    print(f"In Hugging Face Space: {in_hf_space}")
    
    # List available packages without importing them
    try:
        import pkg_resources
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        print(f"Number of installed packages: {len(installed_packages)}")
        print("Key packages:")
        key_packages = ["torch", "transformers", "numpy", "opencv-python", "mediapipe"]
        for pkg in key_packages:
            if pkg in installed_packages:
                try:
                    version = pkg_resources.get_distribution(pkg).version
                    print(f"  ✓ {pkg} (version {version})")
                except:
                    print(f"  ✓ {pkg} (version unknown)")
            else:
                print(f"  ✗ {pkg} (not installed)")
    except Exception as e:
        print(f"Could not list packages: {str(e)}")
    
    return True

def test_basic_functionality():
    """Test basic functionality without importing problematic packages"""
    print("\n===== Testing Basic Functionality =====")
    
    # Test file operations
    try:
        test_file = "octavia_test.txt"
        with open(test_file, "w") as f:
            f.write("Octavia Opulence³ - Luxury isn't what you have—it's how completely you own who you are.")
        
        with open(test_file, "r") as f:
            content = f.read()
        
        os.remove(test_file)
        print(f"✓ File operations successful")
        print(f"  Read: {content}")
    except Exception as e:
        print(f"✗ File operations failed: {str(e)}")
    
    # Test JSON operations (for data handling)
    try:
        octavia_data = {
            "name": "Octavia Opulence³",
            "signature_feature": "Blue Lipstick",
            "quotes": [
                "Luxury isn't what you have—it's how completely you own who you are.",
                "In a world of beige conformity, wear blue lipstick and make them remember you.",
                "The most exquisite accessory you can wear is your truth."
            ]
        }
        
        json_str = json.dumps(octavia_data, indent=2)
        parsed_data = json.loads(json_str)
        
        print(f"✓ JSON operations successful")
        print(f"  Quotes: {len(parsed_data['quotes'])}")
    except Exception as e:
        print(f"✗ JSON operations failed: {str(e)}")
    
    return True

def suggest_next_steps():
    """Suggest next steps based on test results"""
    print("\n===== Suggested Next Steps =====")
    
    print("1. Fix dependency issues:")
    print("   - Try: pip install setuptools==65.5.0")
    print("   - Or: conda create -n octavia_env python=3.10")
    
    print("\n2. For language model component:")
    print("   - Try: pip install transformers torch")
    print("   - Test with: from transformers import pipeline")
    
    print("\n3. For facial modeling component:")
    print("   - Try: pip install numpy==1.24.3 opencv-python==4.8.0.76")
    print("   - Test with: import cv2; import numpy")
    
    print("\n4. If issues persist, consider:")
    print("   - Using a different base image for your Space")
    print("   - Implementing components separately")
    print("   - Using pre-trained models instead of training in the Space")

if __name__ == "__main__":
    print("=================================================")
    print("  Octavia Opulence³ Minimal Environment Test")
    print("=================================================")
    
    start_time = time.time()
    
    # Test environment
    environment_success = test_environment()
    
    # Test basic functionality
    functionality_success = test_basic_functionality()
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    seconds = int(elapsed_time)
    
    # Print summary
    print("\n=================================================")
    print("Test Summary:")
    print(f"Environment Check: {'✓ Completed' if environment_success else '✗ Failed'}")
    print(f"Basic Functionality: {'✓ Completed' if functionality_success else '✗ Failed'}")
    print(f"Test completed in {seconds}s")
    print("=================================================")
    
    # Suggest next steps
    suggest_next_steps()
