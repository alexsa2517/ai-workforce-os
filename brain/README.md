# AI Brain

The Brain is the central intelligence module of the AI Workforce OS.

## Location
- **Code:** `backend/app/core/brain.py`
- **Documentation:** This file contains Director AI brain documentation

## Capabilities
- Message processing and response generation
- Context management and memory
- Task analysis and routing
- Multi-provider support (OpenAI, Gemini, DeepSeek)
- Personality and system prompt management

## Usage
```python
from app.core.brain import Brain

brain = Brain(provider="openai")
result = brain.process("Hello, what can you do?")
print(result["response"])
```
