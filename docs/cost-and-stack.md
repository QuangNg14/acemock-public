# AceMock - Cost & Stack Decisions

This app is built to run on the cheapest viable stack in 2026. Every paid dependency degrades gracefully: with no keys the app still runs (offline LLM stub, browser voice, dev anonymous user, billing disabled).

## LLM (text)
Researched mid-2026 pricing (per million tokens):

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | 1M context, cheapest overall |
| DeepSeek V3.2 | $0.14 | $0.28 | cheapest major, default |
| GPT-5 base | $0.625 | $5.00 | ~4-18x more expensive |

**Decision:** default `LLM_PROVIDER=deepseek`. All non-Anthropic providers share one OpenAI-compatible client (`services/llm.py`), so switching to Gemini Flash-Lite or Groq is a one-line env change. The interviewer and grader are short-prompt, structured-output calls, so even at scale the cost per graded mock is a fraction of a cent.

## Voice
| Function | Choice | Price | Why |
|----------|--------|-------|-----|
| TTS | ElevenLabs Flash (`eleven_flash_v2_5`) | $0.10 / 1M chars | cheapest quality TTS at scale |
| STT (server) | Groq Whisper large-v3-turbo | $0.02 / hr | ~18x cheaper than OpenAI Whisper |
| STT (default) | Browser Web Speech API | free | no key needed |

**Decision:** decoupled STT -> LLM -> TTS pipeline instead of a Realtime API. This is the dominant cost-saving pattern in open-source AI-interview projects: the Realtime/voice-to-voice APIs are an order of magnitude more expensive than stitching cheap STT + a cheap text LLM + cheap TTS. The browser handles STT for free by default; ElevenLabs is only called for output, and the frontend falls back to free `speechSynthesis` when no key is set.

## Embeddings
OpenAI `text-embedding-3-small` ($0.02 / M) by default, configurable via `EMBEDDING_BASE_URL` to point at Gemini's free-tier embeddings. Optional; seeding works without it.

## Auth & Billing
- **Clerk** for auth: verified server-side via JWKS (no per-request Clerk API calls = no added latency or cost). Dev mode (no keys) uses a persistent anonymous user so the app is fully usable before keys are added.
- **Stripe** for billing: hosted Checkout + Customer Portal (no Stripe.js bundle, no PCI surface). Webhook is idempotent via a `stripe_events` table.

## Net effect
A graded mock interview costs roughly: ~2-4k tokens of DeepSeek (<$0.002) + optional ~1-2k chars of ElevenLabs (<$0.0002). The free tier (3 mocks/month) is effectively free to serve; Pro and QuantReady are high-margin.
