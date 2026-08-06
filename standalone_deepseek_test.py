#!/usr/bin/env python3
"""
Standalone DeepSeek V4 Test Script
Zero dependencies on the rest of the project.
Use this if the main test suite is blocked by IT policy.
"""
import os
import json
import requests

def test_deepseek_direct(api_key):
    print("\n" + "="*60)
    print("Standalone DeepSeek API Test")
    print("="*60)
    
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! If you can see this, reply with 'DEEPSEEK IS ACTIVE'"}
        ],
        "stream": False
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        print("\n✓ SUCCESS!")
        print(f"Response: {content}")
        print(f"Usage: {result.get('usage')}")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED!")
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Details: {e.response.text}")
        return False

if __name__ == "__main__":
    # Get API key from environment or prompt
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        api_key = input("Please enter your DeepSeek API Key: ").strip()
    
    if api_key:
        test_deepseek_direct(api_key)
    else:
        print("No API key provided. Exiting.")
