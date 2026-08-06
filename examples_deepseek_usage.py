#!/usr/bin/env python3
"""
Examples of using DeepSeek V4 API with AI Workforce OS
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.llm.factory import LLMFactory
from app.core.config import settings


def example_1_basic_chat():
    """Example 1: Basic chat with DeepSeek"""
    print("\n" + "="*60)
    print("Example 1: Basic Chat")
    print("="*60)
    
    client = LLMFactory.get("deepseek")
    
    result = client.generate(
        prompt="What are the top 3 programming languages in 2024?",
        temperature=0.7,
        max_tokens=200
    )
    
    if result.get("error"):
        print(f"Error: {result.get('detail')}")
    else:
        print(f"Response:\n{result.get('content')}")
        print(f"\nTokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")


def example_2_with_system_prompt():
    """Example 2: Chat with system prompt"""
    print("\n" + "="*60)
    print("Example 2: Chat with System Prompt")
    print("="*60)
    
    client = LLMFactory.get("deepseek")
    
    result = client.generate(
        prompt="What is machine learning?",
        system_prompt="You are a computer science professor. Explain concepts clearly and concisely.",
        temperature=0.5,  # Lower temperature for more factual responses
        max_tokens=300
    )
    
    if result.get("error"):
        print(f"Error: {result.get('detail')}")
    else:
        print(f"Response:\n{result.get('content')}")
        print(f"\nTokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")


def example_3_different_models():
    """Example 3: Using different DeepSeek models"""
    print("\n" + "="*60)
    print("Example 3: Different Models")
    print("="*60)
    
    client = LLMFactory.get("deepseek")
    
    # Using flash model (fast, cost-effective)
    print("\nUsing deepseek-v4-flash (fast):")
    result_flash = client.generate(
        prompt="Explain quantum computing in one sentence",
        model="deepseek-v4-flash",
        max_tokens=100
    )
    if not result_flash.get("error"):
        print(f"Response: {result_flash.get('content')}")
    
    # Using pro model (more capable)
    print("\nUsing deepseek-v4-pro (more capable):")
    result_pro = client.generate(
        prompt="Explain quantum computing in one sentence",
        model="deepseek-v4-pro",
        max_tokens=100
    )
    if not result_pro.get("error"):
        print(f"Response: {result_pro.get('content')}")


def example_4_temperature_control():
    """Example 4: Temperature control for different outputs"""
    print("\n" + "="*60)
    print("Example 4: Temperature Control")
    print("="*60)
    
    client = LLMFactory.get("deepseek")
    prompt = "Complete this story: Once upon a time..."
    
    # Low temperature (deterministic)
    print("\nLow temperature (0.2 - deterministic):")
    result_low = client.generate(prompt=prompt, temperature=0.2, max_tokens=50)
    if not result_low.get("error"):
        print(f"Response: {result_low.get('content')}")
    
    # High temperature (creative)
    print("\nHigh temperature (1.5 - creative):")
    result_high = client.generate(prompt=prompt, temperature=1.5, max_tokens=50)
    if not result_high.get("error"):
        print(f"Response: {result_high.get('content')}")


def example_5_list_models():
    """Example 5: List available models"""
    print("\n" + "="*60)
    print("Example 5: Available Models")
    print("="*60)
    
    client = LLMFactory.get("deepseek")
    models = client.list_models()
    
    print("\nAvailable Models:")
    for model in models.get("models", []):
        print(f"  - {model['id']}: {model['description']}")
    
    print("\nDeprecated Models (auto-mapped):")
    for model in models.get("deprecated", []):
        print(f"  - {model['id']} → {model['replacement']} (deprecated {model['deprecated_on']})")


def example_6_all_providers():
    """Example 6: Compare all LLM providers"""
    print("\n" + "="*60)
    print("Example 6: All LLM Providers")
    print("="*60)
    
    prompt = "What is AI?"
    
    for provider in ["openai", "gemini", "deepseek"]:
        print(f"\n{provider.upper()}:")
        try:
            client = LLMFactory.get(provider)
            result = client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )
            
            if result.get("error"):
                print(f"  Error: {result.get('detail')}")
            else:
                print(f"  Response: {result.get('content')[:100]}...")
                print(f"  Tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        except Exception as e:
            print(f"  Exception: {e}")


def example_7_error_handling():
    """Example 7: Error handling"""
    print("\n" + "="*60)
    print("Example 7: Error Handling")
    print("="*60)
    
    client = LLMFactory.get("deepseek")
    
    # Test with invalid model
    print("\nTesting with invalid model:")
    result = client.generate(
        prompt="Hello",
        model="invalid-model-name",
        max_tokens=100
    )
    print(f"Result: {result}")
    
    # Test with very long prompt
    print("\nTesting with very long max_tokens:")
    result = client.generate(
        prompt="Hello",
        max_tokens=100000  # This might fail
    )
    if result.get("error"):
        print(f"Error: {result.get('error')} - {result.get('detail')}")
    else:
        print(f"Success: {len(result.get('content', ''))} characters")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("DeepSeek V4 API Usage Examples")
    print("="*60)
    
    print(f"\nCurrent Configuration:")
    print(f"  API Key set: {'Yes' if settings.DEEPSEEK_API_KEY else 'No'}")
    print(f"  Model: {settings.DEEPSEEK_MODEL}")
    print(f"  Base URL: {settings.DEEPSEEK_BASE_URL}")
    
    if not settings.DEEPSEEK_API_KEY:
        print("\n⚠ WARNING: DEEPSEEK_API_KEY is not set!")
        print("Set it in .env or environment variables to run these examples.")
        print("\nTo set it:")
        print("  export DEEPSEEK_API_KEY=sk-your-key-here")
        print("  python examples_deepseek_usage.py")
        return 1
    
    try:
        example_1_basic_chat()
        example_2_with_system_prompt()
        example_3_different_models()
        example_4_temperature_control()
        example_5_list_models()
        example_6_all_providers()
        example_7_error_handling()
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*60)
    print("✓ All examples completed!")
    print("="*60 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
