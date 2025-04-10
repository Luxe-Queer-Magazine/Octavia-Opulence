#!/usr/bin/env python3
"""
Simple Test Script for Octavia Opulence³ Digital Human Implementation
Language Model Component Only
"""

import os
import sys
import time

def test_language_model():
    """Test the language model component without OpenCV dependencies"""
    print("\n===== Testing Octavia's Language Model Component =====")
    
    try:
        from transformers import pipeline
        print("✓ Successfully imported transformers")
        
        # Create a simple pipeline
        print("Creating text generation pipeline...")
        generator = pipeline('text-generation', model='gpt2')
        
        # Generate text with Octavia's style
        prompts = [
            "Luxury is",
            "The essence of authenticity is",
            "Blue lipstick represents"
        ]
        
        for prompt in prompts:
            print(f"\nPrompt: \"{prompt}\"")
            print("Generating response...")
            result = generator(prompt, max_length=50, num_return_sequences=1)
            print(f"Response: \"{result[0]['generated_text']}\"")
        
        print("\n✅ Language model test completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Error testing language model: {str(e)}")
        return False

if __name__ == "__main__":
    print("=================================================")
    print("  Octavia Opulence³ Simple Language Model Test")
    print("=================================================")
    
    start_time = time.time()
    
    # Test language model
    language_model_success = test_language_model()
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    # Print summary
    print("\n=================================================")
    print("Test Summary:")
    print(f"Language Model Component: {'✅ Success' if language_model_success else '❌ Failed'}")
    print(f"Test completed in {int(minutes)}m {int(seconds)}s")
    print("=================================================")
    
    if language_model_success:
        print("\n✨ Language model test passed! Ready for Octavia's voice training. ✨")
    else:
        print("\n⚠️ Language model test failed. Please check the output for details.")
