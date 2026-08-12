# AI Workforce OS — Testing Strategy

## Goal

Prove the production workflow before connecting real image/video generation APIs.

## Quality gates

1. Frontend: TypeScript and production build must pass.
2. Backend: pytest must pass and health/readiness contracts must remain valid.
3. AI Director: generated output must contain script, scenes, shots, dialogue, characters, and storyboard data.
4. Storyboard: every shot requires description, dialogue, duration, character, and camera.
5. Character consistency: character identity attributes must remain stable across scenes.
6. Approval gate: video generation is not permitted until all preconditions are complete and the user explicitly approves.
7. E2E: the complete Project → Script → Storyboard → Approval workflow must be exercised before real media APIs are enabled.

## Test levels

- Unit tests: deterministic validation functions and contracts.
- API tests: FastAPI health/readiness and endpoint contracts.
- Integration tests: Director output assembled from multiple workflow components.
- E2E tests: user workflow from project creation through approval.
- Quality tests: content completeness and consistency.

## Mock-first rule

No real image/video provider is required for these tests. Media generation should remain behind a provider interface and use deterministic mocks until the quality gates pass.

## CI

GitHub Actions runs backend pytest and frontend type/build checks on the security/workflow branch and pull requests touching the relevant code.
