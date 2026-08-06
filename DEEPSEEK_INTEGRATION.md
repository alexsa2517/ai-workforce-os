# DeepSeek V4 Integration Guide

## Overview

This project has been updated to support **DeepSeek V4 API** (as of July 24, 2026). The legacy model names `deepseek-chat` and `deepseek-reasoner` have been deprecated and automatically mapped to their V4 equivalents.

## Models

### Available DeepSeek V4 Models

| Model ID | Description | Use Case |
|----------|-------------|----------|
| `deepseek-v4-flash` | Efficiency-optimized, 284B MoE, 13B active params | Fast responses, cost-effective |
| `deepseek-v4-pro` | Full capability model with 1.6T parameters | Complex reasoning, high quality |

### Legacy Model Mapping

The following legacy models are automatically mapped to V4 equivalents:

| Legacy Model | Maps To | Deprecated |
|-------------|---------|-----------|
| `deepseek-chat` | `deepseek-v4-flash` | 2026-07-24 |
| `deepseek-reasoner` | `deepseek-v4-pro` | 2026-07-24 |

## Setup

### 1. Get Your DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up or log in
3. Navigate to API keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### 2. Configure Environment

Create or update `.env` file in the project root:

```bash
# DeepSeek Configuration
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

Or set environment variables:

```bash
export DEEPSEEK_API_KEY=sk-your-api-key-here
export DEEPSEEK_MODEL=deepseek-v4-flash
export DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. Install Dependencies

```bash
# Install root dependencies
pip install -r requirements.txt

# Or install backend dependencies specifically
cd backend
pip install -r requirements.txt
```

## Usage

### Using the Chat API

```bash
# Start the backend server
cd backend
uvicorn app.main:app --reload
```

Then make a request to the chat endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "deepseek",
    "message": "What is the capital of France?",
    "model": "deepseek-v4-flash",
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### Using Python

```python
from app.services.llm.factory import LLMFactory

# Get DeepSeek client
client = LLMFactory.get("deepseek")

# Generate response
result = client.generate(
    prompt="What is the capital of France?",
    temperature=0.7,
    max_tokens=100
)

if result.get("error"):
    print(f"Error: {result.get('detail')}")
else:
    print(f"Response: {result.get('content')}")
    print(f"Tokens used: {result.get('usage')}")
```

### Using with System Prompt

```python
client = LLMFactory.get("deepseek")

result = client.generate(
    prompt="What is the capital of France?",
    system_prompt="You are a helpful geography assistant.",
    temperature=0.7,
    max_tokens=100
)
```

### Using Legacy Model Names

```python
# These will automatically map to V4 equivalents
client = LLMFactory.get("deepseek")

# Using legacy name (auto-mapped to deepseek-v4-flash)
result = client.generate(
    prompt="Hello",
    model="deepseek-chat"  # Auto-mapped to deepseek-v4-flash
)

# Using legacy name (auto-mapped to deepseek-v4-pro)
result = client.generate(
    prompt="Complex reasoning task",
    model="deepseek-reasoner"  # Auto-mapped to deepseek-v4-pro
)
```

## Testing

Run the integration test suite:

```bash
# From project root
python test_deepseek_integration.py
```

This will test:
- ✓ Configuration loading
- ✓ DeepSeek client initialization
- ✓ LLM Factory pattern
- ✓ API call (if API key is set)

## API Reference

### DeepSeekClient.generate()

```python
def generate(
    self,
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
```

**Parameters:**
- `prompt` (str): User message
- `model` (Optional[str]): Override model name (supports deepseek-v4-flash, deepseek-v4-pro)
- `temperature` (float): Sampling temperature (0.0-2.0), default 0.7
- `max_tokens` (int): Maximum tokens in response, default 2048
- `system_prompt` (Optional[str]): Optional system prompt

**Returns:**
```python
{
    "content": "Response text",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 50,
        "total_tokens": 60
    }
}
```

**Error Response:**
```python
{
    "content": "",
    "usage": {},
    "error": "api_key_missing",
    "detail": "DEEPSEEK_API_KEY is not configured..."
}
```

### DeepSeekClient.list_models()

```python
def list_models(self) -> Dict[str, Any]:
```

Returns available and deprecated models.

## Error Handling

The client includes comprehensive error handling:

| Error | Cause | Solution |
|-------|-------|----------|
| `api_key_missing` | DEEPSEEK_API_KEY not set | Set API key in .env or environment |
| `timeout` | Request took too long | Increase timeout or retry |
| `api_error` | API returned error | Check API key, rate limits, model name |
| `unexpected` | Unexpected error | Check logs for details |

## Configuration

All settings are in `backend/app/core/config.py`:

```python
DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API key")
DEEPSEEK_MODEL: str = Field(default="deepseek-v4-flash", description="DeepSeek model name")
DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com", description="DeepSeek API base URL")
```

## Troubleshooting

### "DEEPSEEK_API_KEY is not set"

**Solution:** Set the API key in `.env` file or as an environment variable:
```bash
export DEEPSEEK_API_KEY=sk-your-key-here
```

### "Unsupported model: deepseek-v4-flash"

**Solution:** This shouldn't happen. Check that:
1. Your API key is valid
2. The model name is correct
3. Your account has access to the model

### "Request timed out"

**Solution:** The API took too long to respond. Try:
1. Using a simpler prompt
2. Reducing max_tokens
3. Retrying the request

### "Invalid API key"

**Solution:** 
1. Verify your API key is correct
2. Check it hasn't expired
3. Generate a new key from the platform

## Migration from Legacy Models

If you're using legacy model names, they will automatically work:

```python
# Old code (still works, auto-mapped)
result = client.generate(prompt="Hello", model="deepseek-chat")

# New code (recommended)
result = client.generate(prompt="Hello", model="deepseek-v4-flash")
```

## Performance Tips

1. **Use deepseek-v4-flash** for fast, cost-effective responses
2. **Use deepseek-v4-pro** for complex reasoning tasks
3. **Adjust temperature** based on use case:
   - Lower (0.0-0.5): More deterministic, better for factual tasks
   - Higher (0.7-1.0): More creative, better for content generation
4. **Set appropriate max_tokens** to control response length and cost

## Support

For issues or questions:
1. Check the [DeepSeek Documentation](https://api-docs.deepseek.com/)
2. Review error messages and logs
3. Run the test suite: `python test_deepseek_integration.py`
4. Check GitHub issues

## Related Files

- `backend/app/services/llm/deepseek.py` - DeepSeek client implementation
- `backend/app/services/llm/factory.py` - LLM factory pattern
- `backend/app/core/config.py` - Configuration management
- `backend/app/routers/chat.py` - Chat API endpoints
- `.env.example` - Example environment configuration
