# AI Workforce OS

Build the Operating System for AI Employees.

## New: AI Money Lab V1

AI Money Lab turns the existing multi-LLM foundation into a small **AI Venture Studio**. A business brief is sent to independent specialist models in parallel, then a CEO model synthesizes the evidence into a GO / TEST / NO-GO decision and a low-cost validation experiment.

### Default AI team

| Role | Provider | Responsibility |
|---|---|---|
| CEO | OpenAI | Synthesis and final decision |
| Research | Gemini | Market, demand, competitors |
| Business | OpenAI | Offer, customer and GTM |
| Finance | DeepSeek | Unit economics and costs |
| Technology | DeepSeek | MVP architecture |
| Critic | Kimi | Red-team / failure analysis |
| Operator | Manus | Execute validated tasks |

The design deliberately keeps provider adapters separate. If one provider is unavailable, the board can still return the other reports instead of crashing the whole run.

### API

`POST /api/v1/money-lab/run`

```json
{
  "brief": "Build a service for Thai SMEs that automates lead follow-up with AI.",
  "goal": "Reach the first 10,000 THB of revenue with minimal upfront cost"
}
```

`GET /api/v1/money-lab/team` returns the current team and routing.

`POST /api/v1/operator/manus/task` sends an approved execution task to Manus API v2.

### Architecture

```text
User brief
   |
   +--> Research (Gemini) ----+
   +--> Business (OpenAI) ----+
   +--> Finance (DeepSeek) ---+--> CEO synthesis (OpenAI)
   +--> Technology (DeepSeek)-+
   +--> Critic (Kimi) --------+
                                  |
                              GO / TEST / NO-GO
                                  |
                            validation plan
                                  |
                              Manus Operator
```

Manus API v2 supports programmatic tasks, projects, files, webhooks and connectors; this repository uses it as the execution layer after the board reaches a decision. See the official Manus API documentation for current endpoint details.

## Setup

```bash
git clone https://github.com/alexsa2517/ai-workforce-os.git
cd ai-workforce-os
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
```

Fill in API keys for the providers you want to activate. The Money Lab can run with a subset of providers, but a full board requires OpenAI, Gemini, DeepSeek and Kimi; Manus is only required for execution.

Run:

```bash
cd backend
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

## Existing capabilities

The repository also contains DirectorAI, voice/media functionality, a FastAPI backend, database support, and the existing OpenAI/Gemini/DeepSeek LLM factory.

## Security

API keys belong in `.env` or a secret manager, never in source code. If an API key has previously been committed to the repository, rotate/revoke it at the provider before using the system in production.

## License

MIT
