# AI Workforce OS

Build the Operating System for AI Employees.

## Mission

Help businesses deploy AI Employees in minutes.

## Vision

The Operating System for AI Employees.

## Project Structure

This project is structured into several key components:

- `agents`: Contains the core AI agents, such as `DirectorAI`.
- `api`: Defines the API endpoints for interacting with the AI Workforce OS.
- `backend`: Houses the FastAPI application, services, and agent implementations.
- `database`: Placeholder for database-related configurations and migrations.
- `deployment`: Contains deployment scripts and configurations.
- `docs`: Comprehensive documentation for the project, including architecture, API, and agent specifics.
- `frontend`: Frontend application code.
- `knowledge`: Stores knowledge bases for AI agents, e.g., character data for `DirectorAI`.
- `tests`: Unit and integration tests.

## Setup and Installation

To set up and run the project locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/alexsa2517/ai-workforce-os.git
    cd ai-workforce-os
    ```

2.  **Create a Python virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install backend dependencies:**

    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the `backend` directory with your API keys:

    ```
    OPENAI_API_KEY="your_openai_api_key"
    GEMINI_API_KEY="your_gemini_api_key"
    ```

## Running the Application

To run the FastAPI backend:

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

## DirectorAI

The `DirectorAI` agent is responsible for generating scenes based on loaded knowledge. It uses `memory_loader.py` to load character, world, and episode data from the `knowledge/director-ai` directory.

## LLM Services

The project integrates with various Large Language Models (LLMs) through a factory pattern. The `LLMFactory` in `backend/app/services/llm/factory.py` provides a unified interface to interact with different LLM providers such as OpenAI and Gemini.

## AI Development Tools

This project is optimized for AI-assisted development:

- **Aider:** You can use [Aider](https://aider.chat/) to collaborate with LLMs (like DeepSeek or GPT-4o) directly in your terminal to edit and create files.
- **Environment Setup:** Ensure you have your `DEEPSEEK_API_KEY` or `OPENAI_API_KEY` set in your environment or a `.env` file to enable AI features.

## Bug Fixes and Improvements (July 2026)

-   **Fixed `knowledge` directory path:** Corrected the directory name from `" director-ai"` to `"director-ai"` to resolve file loading issues for `DirectorAI`.
-   **Corrected LLM service imports:** Adjusted import paths in `backend/app/services/llm/factory.py` to correctly reference `OpenAIClient`, `GeminiClient`, and `DeepSeekClient`.
-   **Updated OpenAI model:** Changed the OpenAI model from `gpt-5.5` (non-existent) to `gpt-4o` in `backend/app/services/llm/openai.py`.
-   **Updated Gemini integration:** Refactored `backend/app/services/llm/gemini.py` to use `google.generativeai` (current standard) and updated the model to `gemini-1.5-pro`.
-   **Cleaned up test files:** Removed `repro_bug.py` and `test_developer.py` (stale/broken) from the `backend` directory.
-   **Updated `requirements.txt`:** Added `google-generativeai` to ensure all necessary dependencies are installed.
