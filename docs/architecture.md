# AceMock - Architecture

## Stack
- Frontend: Next.js (App Router), React 19, TypeScript, Tailwind v4. Deploy to Vercel.
- Backend: FastAPI, SQLAlchemy async, Alembic, Postgres + pgvector. Deploy via Docker.
- LLM: one OpenAI-compatible client (default DeepSeek V3.2; Gemini/Groq/OpenAI/Anthropic via env), with an offline deterministic stub.
- Voice: ElevenLabs Flash TTS + Groq Whisper STT, with browser Web Speech / speechSynthesis as the free fallback.
- Auth: Clerk (JWKS-verified). Payments: Stripe (hosted Checkout + Portal). File storage: Cloudflare R2.

See `cost-and-stack.md` for the pricing analysis behind these choices.

## Backend layering
```
api/        FastAPI routers (questions, mock, behavioral, quant, voice, billing, health)
  -> services/   logic (interviewer, grader, llm, embeddings, voice, auth, billing)
    -> models/   SQLAlchemy entities
ai/prompts/  prompt builders (never inline in services)
alembic/     migrations (baseline creates pgvector + all tables + ivfflat index)
scripts/     init_db, seed_rubrics, seed_vault, seed_quant, backfill_embeddings
```

## Core domain model
- `Question` - real seeded question (company, track, round, difficulty, prompt, Pro-gated solution, embedding).
- `Rubric` + `RubricCriterion` - the mentor answer key: weighted criteria with anchored 1/3/5 levels plus an ordered hint ladder.
- `MockSession` + `MockTurn` + `Scorecard` - one interview, its transcript, and the graded result.
- `BehavioralStory` + `BehavioralDrill` - STAR stories, value mapping, graded drills.
- `QuantDrill` + `QuantAttempt` - quant items by category/firm and attempt history.
- `User` - entitlement mirror (Clerk owns identity, Stripe owns billing).

## The two engines
### Interviewer (`services/interviewer.py`)
Builds the system prompt from the seeded question + the rubric's hint ladder. Releases the next ladder rung only when the candidate stalls on two consecutive turns. Never reveals the full solution. Increments `hints_used`, which the grader penalizes.

### Grader (`services/grader.py`)
Sends the rubric criteria (with anchors) and the full transcript to the model, then recomputes the weighted overall from the returned breakdown so the score is internally consistent. Buckets a recommendation if the model omits one. Always grades against a rubric; it never free-scores.

## Retrieval
Questions carry a pgvector embedding (text-embedding-3-small, 1536 dims) with an IVFFlat cosine index, enabling "similar questions" and semantic company-question lookup as the bank grows.

## Runnability without keys
The LLM client returns schema-valid stub responses when no API key is set, so `seed -> start -> message -> grade` works end to end locally and in CI. Wire real keys in `.env` to switch to live models.

## Data flow (mock)
```
POST /mock/start    pick question + rubric -> create session -> opening interviewer turn
POST /mock/{id}/message  append candidate turn -> interviewer reply (maybe a hint)
POST /mock/{id}/grade    rubric-grade transcript -> persist + return scorecard
```

## Auth (Clerk)
`services/auth.py` exposes `current_user_optional`, `require_user`, and `require_pro`
dependencies. Tokens are verified locally against Clerk's JWKS (no per-request Clerk
API call). When Clerk env vars are unset the app runs in dev mode with a persistent
anonymous user, so every endpoint stays usable. The frontend bridges the Clerk token
into the fetch client via `lib/auth-bridge.ts` + `components/TokenBridge.tsx`, and only
mounts `ClerkProvider`/`clerkMiddleware` when a publishable key is present.

## Billing (Stripe) and gating
`services/billing.py` creates hosted Checkout and Customer Portal sessions and handles
the webhook idempotently via the `stripe_events` table (`checkout.session.completed` and
subscription lifecycle events flip `user.is_pro`). Gating is server-enforced:
- Free tier: `FREE_MONTHLY_MOCKS` graded mocks per calendar month (counted in `mock/start`).
- Pro-only: `GET /questions/{id}/solution` and `GET /quant/drills/{id}/solution` (`require_pro`).

## Voice (cost-optimized)
`services/voice.py` + `api/voice.py`: `POST /voice/tts` returns ElevenLabs Flash MP3,
`POST /voice/stt` transcribes via Groq Whisper. Both return 503 when unconfigured so the
frontend uses the free browser Web Speech API (input) and `speechSynthesis` (output).
The pipeline is decoupled STT -> LLM -> TTS, which is far cheaper than a Realtime API.
