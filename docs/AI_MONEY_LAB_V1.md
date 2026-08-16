# AI Money Lab V1

## Mission
Build a multi-model business evaluation and portfolio engine whose **minimum** monthly revenue requirement is THB 1,000,000. There is no upper revenue ceiling.

## Roles
- OpenAI: CEO / final strategic recommendation
- Gemini: market intelligence
- DeepSeek: finance, engineering feasibility and adversarial critique
- Future adapters: Kimi, Claude, Manus and other providers

## Workflow
1. Submit a business opportunity.
2. Market agent researches demand, customers, competitors and pricing.
3. Finance/engineering agent estimates economics and feasibility.
4. Critic attacks assumptions and identifies failure modes.
5. CEO produces BUILD / TEST / KILL recommendation.
6. Portfolio endpoint aggregates real monthly revenue and calculates the gap to THB 1M.

## API
- `GET /api/v1/money-lab/target`
- `POST /api/v1/money-lab/evaluate`
- `POST /api/v1/money-lab/portfolio`

## Important rule
Hypothetical market size is not revenue. Revenue counts only when it is backed by actual customer/payment evidence.
