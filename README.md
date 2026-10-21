# AceMock

AI mock-interview platform that turns real, company-specific question banks into a **graded, recurring-revenue product**. Unlike resume tools or passive question databases, AceMock runs a live AI interview and grades you against a **calibrated mentor rubric** (hint ladder + scoring weights), not a generic LLM opinion.

One product, three surfaces:

| Surface | What it does | Audience |
|---------|--------------|----------|
| **Mock Agent** | Live coding + system-design interviews using real questions for a target company/role, graded by the mentor rubric | Every SWE/Data candidate |
| **Behavioral Engine** | Turns raw experiences into a STAR story bank mapped to each company's values/LPs, then drills with the behavioral rubric | Strong coders who fail behavioral |
| **QuantReady** | Brainteaser, probability, mental-math, and market-making drills with firm-specific tracks | High-intent IB/quant audience |

## Why it wins

- **Moat 1 - real banks:** seeded from 100+ companies' actual OA + interview questions (SWE, Data, Quant).
- **Moat 2 - the grader:** a mentor-calibrated rubric with a hint ladder and scoring weights, so feedback is an answer key, not a vibe.
- **Moat 3 - distribution:** launched through an existing 16,750-member career community with a decoded viral-content formula.

## Architecture

Monorepo mirroring the proven HireReady stack, tuned for the **cheapest viable 2026 stack** (see [`docs/cost-and-stack.md`](docs/cost-and-stack.md)):

- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind v4 (`frontend/`)
- **Backend:** FastAPI, SQLAlchemy async, Alembic, pgvector (`backend/`)
- **LLM:** one OpenAI-compatible client, default **DeepSeek V3.2** (cheapest major); swap to Gemini Flash-Lite / Groq / OpenAI / Anthropic via one env var
- **Voice:** **ElevenLabs Flash** TTS + **Groq Whisper** STT (browser Web Speech API as the free default), a decoupled pipeline far cheaper than Realtime APIs
- **Auth:** Clerk (JWKS-verified) - **Payments:** Stripe (hosted Checkout + Portal, idempotent webhook) - **Storage:** Postgres/pgvector + Cloudflare R2

Everything degrades gracefully: with no keys the app still runs (offline LLM stub, browser voice fallback, dev anonymous user, billing disabled). You only fill env vars.

See [`docs/architecture.md`](docs/architecture.md), [`docs/product-spec.md`](docs/product-spec.md) and [`docs/cost-and-stack.md`](docs/cost-and-stack.md).

## Quickstart

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env                            # fill in DATABASE_URL (+ optional keys)
alembic upgrade head                              # or: python scripts/init_db.py
python scripts/seed_rubrics.py                    # required: grading rubrics
python scripts/seed_quant.py                      # quant drills
python scripts/seed_vault.py --vault "/path/to/your-vault" --limit 200
python scripts/backfill_embeddings.py             # optional: semantic search (needs embedding key)
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Backend serves on `http://localhost:8000` (docs at `/docs`), frontend on `http://localhost:3000`.

## Repo layout

```
backend/    FastAPI service: models, api, services, ai/prompts, alembic, scripts
frontend/   Next.js app: app router pages (mock/behavioral/quant), api client
docs/       product spec, architecture, seeding guide
```
