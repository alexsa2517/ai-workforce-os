#!/usr/bin/env python3
"""
Test script for DeepSeek V4 API integration
Tests the DeepSeek client and LLM factory
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_deepseek_client():
    """Test DeepSeek client initialization and basic functionality"""
    print("\n" + "="*60)
    print("Testing DeepSeek Client")
    print("="*60)
    
    try:
        from app.services.llm.deepseek import DeepSeekClient
        print("✓ Successfully imported DeepSeekClient")
    except ImportError as e:
        print(f"✗ Failed to import DeepSeekClient: {e}")
        return False
    
    try:
        client = DeepSeekClient()
        print("✓ Successfully initialized DeepSeekClient")
    except Exception as e:
        print(f"✗ Failed to initialize DeepSeekClient: {e}")
        return False
    
    # Test model resolution
    print("\nTesting model resolution:")
    print(f"  Default model: {client.model}")
    print(f"  Legacy 'deepseek-chat' -> {client._resolve_model('deepseek-chat')}")
    print(f"  Legacy 'deepseek-reasoner' -> {client._resolve_model('deepseek-reasoner')}")
    
    # Test list models
    print("\nAvailable models:")
    models = client.list_models()
    for model in models.get("models", []):
        print(f"  - {model['id']}: {model['description']}")
    
    print("\nDeprecated models:")
    for model in models.get("deprecated", []):
        print(f"  - {model['id']} (deprecated {model['deprecated_on']}) -> {model['replacement']}")
    
    return True


def test_llm_factory():
    """Test LLM Factory pattern"""
    print("\n" + "="*60)
    print("Testing LLM Factory")
    print("="*60)
    
    try:
        from app.services.llm.factory import LLMFactory
        print("✓ Successfully imported LLMFactory")
    except ImportError as e:
        print(f"✗ Failed to import LLMFactory: {e}")
        return False
    
    try:
        deepseek_client = LLMFactory.get("deepseek")
        print("✓ Successfully got DeepSeek client from factory")
        print(f"  Client type: {type(deepseek_client).__name__}")
    except Exception as e:
        print(f"✗ Failed to get DeepSeek client from factory: {e}")
        return False
    
    try:
        openai_client = LLMFactory.get("openai")
        print("✓ Successfully got OpenAI client from factory")
    except Exception as e:
        print(f"✗ Failed to get OpenAI client from factory: {e}")
        return False
    
    try:
        gemini_client = LLMFactory.get("gemini")
        print("✓ Successfully got Gemini client from factory")
    except Exception as e:
        print(f"✗ Failed to get Gemini client from factory: {e}")
        return False
    
    return True


def test_config():
    """Test configuration loading"""
    print("\n" + "="*60)
    print("Testing Configuration")
    print("="*60)
    
    try:
        from app.core.config import settings
        print("✓ Successfully loaded settings")
        
        print(f"\nDeepSeek Configuration:")
        print(f"  API Key set: {'Yes' if settings.DEEPSEEK_API_KEY else 'No'}")
        print(f"  Model: {settings.DEEPSEEK_MODEL}")
        print(f"  Base URL: {settings.DEEPSEEK_BASE_URL}")
        
        print(f"\nOpenAI Configuration:")
        print(f"  API Key set: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
        print(f"  Model: {settings.OPENAI_MODEL}")
        
        print(f"\nGemini Configuration:")
        print(f"  API Key set: {'Yes' if settings.GOOGLE_API_KEY else 'No'}")
        print(f"  Model: {settings.GEMINI_MODEL}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False


def test_deepseek_api_call():
    """Test actual DeepSeek API call (requires valid API key)"""
    print("\n" + "="*60)
    print("Testing DeepSeek API Call")
    print("="*60)
    
    try:
        from app.services.llm.deepseek import DeepSeekClient
        from app.core.config import settings
        
        if not settings.DEEPSEEK_API_KEY:
            print("⚠ DEEPSEEK_API_KEY not set - skipping API call test")
            print("  To test, set DEEPSEEK_API_KEY in .env or environment")
            return True
        
        client = DeepSeekClient()
        print("Testing with prompt: 'Hello, what is 2+2?'")
        
        result = client.generate(
            prompt="What is 2+2?",
            temperature=0.7,
            max_tokens=100
        )
        
        if result.get("error"):
            print(f"✗ API Error: {result.get('detail', result.get('error'))}")
            return False
        
        print("✓ Successfully called DeepSeek API")
        print(f"  Response: {result.get('content', '')[:100]}...")
        print(f"  Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to call DeepSeek API: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DeepSeek V4 Integration Test Suite")
    print("="*60)
    
    results = {
        "Config": test_config(),
        "DeepSeek Client": test_deepseek_client(),
        "LLM Factory": test_llm_factory(),
        "API Call": test_deepseek_api_call(),
    }
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    print("\n" + ("="*60))
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
