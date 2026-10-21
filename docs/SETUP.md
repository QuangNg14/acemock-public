# AceMock - Complete Setup Guide

This is the exact, end-to-end guide to make AceMock fully functional: every service, every link, every environment variable, and how to obtain each value.

## How the app degrades (what you need vs. what is optional)

The app runs with **zero keys** (offline LLM stub, browser voice, dev anonymous user, billing disabled). Each key unlocks real functionality:

| You want | You must configure |
|----------|--------------------|
| App to run at all | `DATABASE_URL` only |
| Real interviewer + grading quality | LLM key (`LLM_API_KEY`, default DeepSeek) |
| Semantic "similar questions" search | `EMBEDDING_API_KEY` |
| Spoken interviewer (voice output) | `ELEVENLABS_API_KEY` |
| Server speech-to-text (optional; browser STT is free) | `GROQ_API_KEY` |
| Real user accounts / sign-in | Clerk keys (frontend + backend) |
| Payments, Pro, QuantReady tiers | Stripe keys + price IDs + webhook |

---

## Prerequisites

- Python 3.12, Node.js 20+, and either Docker (for local Postgres) or a Supabase project.
- The repo cloned locally.

---

## Step 1 - Database (pick ONE)

You need Postgres with the `pgvector` extension.

### Option A - Local via Docker (fastest)
```bash
docker run -d --name acemock-db \
  -e POSTGRES_USER=acemock -e POSTGRES_PASSWORD=acemock -e POSTGRES_DB=acemock \
  -p 5432:5432 pgvector/pgvector:pg16
```
`DATABASE_URL=postgresql+asyncpg://acemock:acemock@localhost:5432/acemock`

### Option B - Supabase (free, hosted)
1. Create a project at https://supabase.com/dashboard
2. Project Settings -> Database -> Connection string -> URI. Copy it.
3. Convert it to the asyncpg driver: change `postgresql://` to `postgresql+asyncpg://`.
4. `pgvector` is preinstalled on Supabase; the baseline migration enables it.

---

## Step 2 - Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate           # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env
# ... edit .env (see Step 4 for every variable) ...

# Create schema (choose one):
alembic upgrade head              # production path
python scripts/init_db.py         # quick local path

# Seed data:
python scripts/seed_rubrics.py                                   # REQUIRED for grading
python scripts/seed_quant.py                                     # quant drills
python scripts/seed_vault.py --vault "/path/to/your-vault" --limit 300
python scripts/backfill_embeddings.py                            # optional (needs embedding key)

uvicorn app.main:app --reload     # serves http://localhost:8000  (API docs at /docs)
```

---

## Step 3 - Frontend

```bash
cd frontend
npm install
copy .env.example .env.local      # macOS/Linux: cp .env.example .env.local
# ... edit .env.local (see Step 4) ...
npm run dev                       # serves http://localhost:3000
```

---

## Step 4 - Get every key (service by service)

### 4.1 LLM (text) - default DeepSeek (cheapest major)
1. Sign up at https://platform.deepseek.com
2. Top up a few dollars (DeepSeek requires prepaid credit).
3. API keys -> Create new key.
4. In `backend/.env`:
   ```
   LLM_PROVIDER=deepseek
   LLM_API_KEY=sk-...          # your DeepSeek key
   ```
   The base URL (`https://api.deepseek.com`) and model (`deepseek-chat`) are preset.

**Cheaper/alternative providers (one-line swap):**
- **Gemini 2.5 Flash-Lite** (free tier available): key at https://aistudio.google.com/app/apikey -> set `LLM_PROVIDER=gemini`, `LLM_API_KEY=...`
- **Groq** (fast, free tier): key at https://console.groq.com/keys -> set `LLM_PROVIDER=groq`, `LLM_API_KEY=gsk_...`
- **OpenAI**: key at https://platform.openai.com/api-keys -> set `LLM_PROVIDER=openai`, `LLM_API_KEY=sk-...`
- **Anthropic**: set `LLM_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=sk-ant-...`

### 4.2 Embeddings (optional - enables semantic search)
- **OpenAI (default):** https://platform.openai.com/api-keys
  ```
  EMBEDDING_API_KEY=sk-...
  EMBEDDING_BASE_URL=https://api.openai.com/v1
  EMBEDDING_MODEL=text-embedding-3-small
  EMBEDDING_DIM=1536
  ```
- **Gemini free alternative:** use a Google AI Studio key, set
  `EMBEDDING_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai`,
  `EMBEDDING_MODEL=text-embedding-004`, `EMBEDDING_DIM=768`.
  (If you change `EMBEDDING_DIM`, recreate the schema before seeding.)

After setting a key: `python scripts/backfill_embeddings.py`.

### 4.3 Voice output - ElevenLabs (TTS)
1. Sign up at https://elevenlabs.io
2. Profile (bottom-left avatar) -> "API Keys" -> create a key.
3. Pick a voice: https://elevenlabs.io/app/voice-library -> open a voice -> "ID" (or use the default Rachel `21m00Tcm4TlvDq8ikWAM`).
4. In `backend/.env`:
   ```
   ELEVENLABS_API_KEY=...
   ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
   ELEVENLABS_MODEL=eleven_flash_v2_5
   ```
Without this, "Voice mode" still works using the free browser `speechSynthesis` voice.

### 4.4 Voice input - Groq Whisper (optional server STT)
- Default speech-to-text uses the **free browser Web Speech API** (Chrome/Edge). No key needed.
- For server-side STT, reuse a Groq key from https://console.groq.com/keys:
  ```
  GROQ_API_KEY=gsk_...
  GROQ_STT_MODEL=whisper-large-v3-turbo
  ```

### 4.5 Authentication - Clerk
1. Create an app at https://dashboard.clerk.com
2. **API keys** (Configure -> API keys):
   - Copy the **Publishable key** (`pk_test_...`) -> frontend `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - Copy the **Secret key** (`sk_test_...`) -> frontend `CLERK_SECRET_KEY` and backend `CLERK_SECRET_KEY`
3. **Frontend API URL** (same page, "Show API URLs" / "Frontend API"): looks like `https://<your-slug>.clerk.accounts.dev`.
   - Backend `CLERK_ISSUER=https://<your-slug>.clerk.accounts.dev`
   - Backend `CLERK_JWKS_URL=https://<your-slug>.clerk.accounts.dev/.well-known/jwks.json`
4. Backend enforces auth only when BOTH `CLERK_ISSUER` and `CLERK_JWKS_URL` are set. Until then it uses a dev anonymous user.

How it wires together: the frontend mounts `ClerkProvider` + `clerkMiddleware` only when the publishable key is present, gets the session token via `useAuth().getToken()`, and the bridge attaches it as `Authorization: Bearer <token>`. The backend verifies that token against Clerk's JWKS (no per-request Clerk API call).

### 4.6 Billing - Stripe
1. Create an account at https://dashboard.stripe.com (use Test mode while developing).
2. **Secret key:** Developers -> API keys -> Secret key (`sk_test_...`) -> backend `STRIPE_SECRET_KEY`.
3. **Create products + prices** (Product catalog -> Add product). Make each a **recurring** price:
   - "AceMock Pro" -> copy its price id (`price_...`) -> `STRIPE_PRICE_PRO`
   - "QuantReady" -> copy its price id -> `STRIPE_PRICE_QUANT`
4. **Webhook signing secret:**
   - **Local dev:** install the Stripe CLI (https://docs.stripe.com/stripe-cli), then:
     ```bash
     stripe login
     stripe listen --forward-to localhost:8000/billing/webhook
     ```
     It prints `whsec_...` -> `STRIPE_WEBHOOK_SECRET`.
   - **Production:** Developers -> Webhooks -> Add endpoint -> URL `https://<your-api>/billing/webhook`, select events:
     `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`.
     Reveal the signing secret (`whsec_...`) -> `STRIPE_WEBHOOK_SECRET`.
5. Success/cancel URLs (already defaulted; change for prod):
   ```
   BILLING_SUCCESS_URL=http://localhost:3000/?upgraded=1
   BILLING_CANCEL_URL=http://localhost:3000/pricing
   ```

---

## Step 5 - Full environment variable reference

### `backend/.env`
| Variable | Required? | Example / default | Purpose |
|----------|-----------|-------------------|---------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://acemock:acemock@localhost:5432/acemock` | Postgres + pgvector |
| `LLM_PROVIDER` | For real AI | `deepseek` | deepseek/gemini/groq/openai/together/anthropic |
| `LLM_API_KEY` | For real AI | `sk-...` | key for the chosen provider (not anthropic) |
| `LLM_BASE_URL` | No | (blank) | override provider preset |
| `LLM_MODEL` | No | (blank) | override provider model |
| `ANTHROPIC_API_KEY` | If provider=anthropic | `sk-ant-...` | |
| `ANTHROPIC_MODEL` | No | `claude-haiku-4.5` | |
| `EMBEDDING_API_KEY` | For search | `sk-...` | embeddings provider key |
| `EMBEDDING_BASE_URL` | No | `https://api.openai.com/v1` | |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | |
| `EMBEDDING_DIM` | No | `1536` | must match model output dim |
| `ELEVENLABS_API_KEY` | For voice out | | TTS |
| `ELEVENLABS_VOICE_ID` | No | `21m00Tcm4TlvDq8ikWAM` | |
| `ELEVENLABS_MODEL` | No | `eleven_flash_v2_5` | |
| `GROQ_API_KEY` | For server STT | `gsk_...` | optional |
| `GROQ_STT_MODEL` | No | `whisper-large-v3-turbo` | |
| `CLERK_SECRET_KEY` | For auth | `sk_test_...` | |
| `CLERK_ISSUER` | For auth | `https://<slug>.clerk.accounts.dev` | token issuer |
| `CLERK_JWKS_URL` | For auth | `https://<slug>.clerk.accounts.dev/.well-known/jwks.json` | |
| `STRIPE_SECRET_KEY` | For billing | `sk_test_...` | |
| `STRIPE_WEBHOOK_SECRET` | For billing | `whsec_...` | |
| `STRIPE_PRICE_PRO` | For billing | `price_...` | Pro plan |
| `STRIPE_PRICE_QUANT` | For billing | `price_...` | QuantReady plan |
| `BILLING_SUCCESS_URL` | No | `http://localhost:3000/?upgraded=1` | |
| `BILLING_CANCEL_URL` | No | `http://localhost:3000/pricing` | |
| `FREE_MONTHLY_MOCKS` | No | `3` | free tier graded-mock cap |
| `FRONTEND_ORIGIN` | Yes | `http://localhost:3000` | CORS allow-list |

### `frontend/.env.local`
| Variable | Required? | Example | Purpose |
|----------|-----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | backend base URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | For auth | `pk_test_...` | enables Clerk UI + tokens |
| `CLERK_SECRET_KEY` | For auth | `sk_test_...` | Clerk middleware |

---

## Step 6 - Verify each feature

With backend + frontend running:

1. **Core (no keys):** open http://localhost:3000 -> Mock Agent -> Start -> send a message -> Finish & grade. You get a scorecard (offline stub) -> confirms wiring.
2. **Real LLM:** set `LLM_API_KEY`, restart backend, run a mock; replies and grading are now model-generated.
3. **Voice:** enable "Voice mode" on the mock page. With `ELEVENLABS_API_KEY` you hear ElevenLabs; without it, the browser voice. Click "Speak" to dictate (Chrome/Edge).
4. **Auth:** set Clerk keys on both sides, restart both. "Sign in" appears in the header; sign in; calls now carry your identity.
5. **Billing:** with Stripe configured and the webhook listener running, go to /pricing -> Upgrade to Pro -> complete Stripe test checkout (card `4242 4242 4242 4242`, any future date/CVC). The webhook flips your account to Pro; solution endpoints and unlimited mocks unlock.
6. **Free limit:** as a non-Pro user, start 4 mocks in a month; the 4th returns a 402 with an upgrade prompt.

API reference: http://localhost:8000/docs

---

## Step 7 - Deploy (optional)

- **Frontend:** Vercel. Set `NEXT_PUBLIC_API_URL` to your deployed API, plus the two Clerk vars.
- **Backend:** Docker image (`backend/Dockerfile`) on Render/Fly/Azure Container Apps. Set all `backend/.env` vars. Run `alembic upgrade head` on deploy.
- **Database:** Supabase (managed pgvector).
- After deploy: update `FRONTEND_ORIGIN`, `BILLING_SUCCESS_URL`, `BILLING_CANCEL_URL`, and the Stripe webhook endpoint URL to your production domains.
