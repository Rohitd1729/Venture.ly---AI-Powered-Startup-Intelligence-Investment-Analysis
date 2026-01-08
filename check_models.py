"""
Diagnostic Script to Check Available Gemini Models

Run this script to see which models are available with your API key.
Save as: check_models.py
Run: python check_models.py
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

def check_models():
    """Check which Gemini models are available"""
    print("=" * 60)
    print("Gemini Model Diagnostic")
    print("=" * 60)
    
    # Load API key
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return
    
    print(f"[OK] API Key found: {api_key[:10]}...")
    print()
    
    try:
        # Configure API
        genai.configure(api_key=api_key)
        print("[OK] API configured successfully")
        print()
        
        # List all models
        print("Available Models:")
        print("-" * 60)
        
        models = list(genai.list_models())
        
        if not models:
            print("❌ No models found")
            return
        
        gemini_models = []
        for m in models:
            if 'gemini' in m.name.lower():
                supports_generate = 'generateContent' in m.supported_generation_methods
                status = "[OK] USABLE" if supports_generate else "[X] NOT FOR GENERATION"
                
                print(f"{status}")
                print(f"  Model: {m.name}")
                print(f"  Methods: {', '.join(m.supported_generation_methods)}")
                print()
                
                if supports_generate:
                    gemini_models.append(m.name)
        
        print("=" * 60)
        print(f"Found {len(gemini_models)} usable Gemini models")
        print("=" * 60)
        
        if gemini_models:
            print("\nRecommended model names to use:")
            for model_name in gemini_models[:3]:
                # Try both with and without 'models/' prefix
                base_name = model_name.replace('models/', '')
                print(f"  • '{model_name}' or '{base_name}'")
        
        print()
        print("=" * 60)
        print("Testing First Available Model")
        print("=" * 60)
        
        if gemini_models:
            test_model_name = gemini_models[0]
            print(f"Testing: {test_model_name}")
            
            try:
                model = genai.GenerativeModel(test_model_name)
                response = model.generate_content("Say 'Hello, I am working!'")
                
                if response and response.text:
                    print(f"[OK] SUCCESS: {response.text}")
                    print()
                    print(f"Use this model in your code: '{test_model_name}'")
                else:
                    print("❌ Model responded but with empty text")
                    
            except Exception as e:
                print(f"❌ Test failed: {e}")
                print()
                print("Trying without 'models/' prefix...")
                
                # Try without prefix
                try:
                    alt_name = test_model_name.replace('models/', '')
                    model = genai.GenerativeModel(alt_name)
                    response = model.generate_content("Say 'Hello, I am working!'")
                    
                    if response and response.text:
                        print(f"[OK] SUCCESS with '{alt_name}': {response.text}")
                        print()
                        print(f"Use this model in your code: '{alt_name}'")
                    
                except Exception as e2:
                    print(f"❌ Also failed: {e2}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Possible issues:")
        print("  1. Invalid API key")
        print("  2. No internet connection")
        print("  3. API key doesn't have access to Gemini models")
        print("  4. Quota exceeded")


if __name__ == "__main__":
    check_models()
