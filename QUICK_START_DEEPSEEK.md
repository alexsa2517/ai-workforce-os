# Quick Start: DeepSeek V4 Integration

## 5-Minute Setup

### Step 1: Get API Key (1 minute)
1. Go to https://platform.deepseek.com/
2. Sign up or log in
3. Create API key
4. Copy the key (starts with `sk-`)

### Step 2: Configure (1 minute)
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and set your DeepSeek API key
DEEPSEEK_API_KEY=sk-your-key-here
```

### Step 3: Install (2 minutes)
```bash
# Install dependencies
pip install -r requirements.txt
```

### Step 4: Test (1 minute)
```bash
# Run the test suite
python test_deepseek_integration.py
```

## Using DeepSeek

### Option A: Chat API (Recommended)

```bash
# Start the server
cd backend
uvicorn app.main:app --reload
```

Then in another terminal:
```bash
# Send a chat request
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "deepseek",
    "message": "Hello, how are you?",
    "model": "deepseek-v4-flash"
  }'
```

### Option B: Python Script

```python
from app.services.llm.factory import LLMFactory

client = LLMFactory.get("deepseek")
result = client.generate(prompt="Hello!")
print(result.get("content"))
```

### Option C: Examples

```bash
# Run example scripts
python examples_deepseek_usage.py
```

## Common Issues

### "DEEPSEEK_API_KEY is not set"
```bash
# Set the environment variable
export DEEPSEEK_API_KEY=sk-your-key-here
```

### "Invalid API key"
1. Check your key is correct
2. Verify it hasn't expired
3. Generate a new key from the platform

### "Request timed out"
- Try with a simpler prompt
- Reduce max_tokens
- Retry the request

## Next Steps

1. **Read the full guide**: `DEEPSEEK_INTEGRATION.md`
2. **Check examples**: `examples_deepseek_usage.py`
3. **Run tests**: `python test_deepseek_integration.py`
4. **Explore the code**: `backend/app/services/llm/deepseek.py`

## Models

- **deepseek-v4-flash**: Fast, cost-effective (recommended for most tasks)
- **deepseek-v4-pro**: More capable, better for complex reasoning

## Support

- Full documentation: `DEEPSEEK_INTEGRATION.md`
- Test suite: `python test_deepseek_integration.py`
- Examples: `python examples_deepseek_usage.py`
