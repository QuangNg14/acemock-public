# AceMock - Engineering Conventions

## Stack
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS v4, Clerk
- **Backend**: FastAPI, SQLAlchemy (async), Alembic, pgvector
- **LLM**: one OpenAI-compatible client (default DeepSeek V3.2; Gemini/Groq/OpenAI/Anthropic via env)
- **Voice**: ElevenLabs Flash TTS + Groq Whisper STT (browser Web Speech / speechSynthesis fallback)
- **Auth**: Clerk (JWKS-verified) - **Payments**: Stripe (hosted Checkout + Portal) - **Storage**: Postgres/pgvector + Cloudflare R2

## Commands
- Backend dev: `cd backend && uvicorn app.main:app --reload`
- Backend lint: `cd backend && ruff check .`
- Backend test: `cd backend && pytest`
- Backend migrate: `cd backend && alembic upgrade head` (or `python scripts/init_db.py`)
- Seed: `python scripts/seed_rubrics.py`, `seed_quant.py`, `seed_vault.py --vault <path>`, `backfill_embeddings.py`
- Frontend dev: `cd frontend && npm run dev`
- Frontend build: `cd frontend && npm run build`

## Architecture
- Monorepo: `frontend/` (Next.js) + `backend/` (FastAPI).
- Backend layered: `api/` (routes) -> `services/` (logic) -> `models/` (SQLAlchemy).
- LLM prompts live in `backend/app/ai/prompts/` as plain string builders, never inline in services.
- DB migrations in `backend/alembic/versions/`.
- Frontend API client in `frontend/src/lib/api.ts`; pages in `frontend/src/app/`.

## Domain model (the moat)
- `Question`: real interview/OA question for a company+role, with `track` (swe/data/quant), `round`, `difficulty`.
- `Rubric` + `RubricCriterion`: the mentor scoring key (weighted criteria + hint ladder). The grader never free-scores; it always grades against a rubric.
- `MockSession` + `MockTurn` + `Scorecard`: one live interview, its turns, and the graded result.
- `BehavioralStory`: a STAR story mapped to company values/LPs, with drill history.
- `QuantDrill`: brainteaser/probability/mental-math/market-making item with firm tracks.

## Conventions
- Type hints on every Python signature; `logging` not `print`; `pathlib` over `os.path`.
- Pydantic v2 schemas for all request/response bodies.
- One public class per file where practical; filename matches the type.
- Never leak full solutions for locked questions through the API (Pro-gated, server-enforced).
- No em dashes in any user-facing copy or docs. Use commas, colons, parentheses.
- Comments explain non-obvious *why*, never the *what*. No iteration/narration comments.
