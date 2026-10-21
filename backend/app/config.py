from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# OpenAI-compatible provider presets: base_url + a sensible cheap default model.
# DeepSeek and Gemini Flash-Lite are the most cost-effective as of 2026.
LLM_PRESETS: dict[str, dict[str, str]] = {
    "deepseek": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash-lite",
    },
    "groq": {"base_url": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile"},
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-5-mini"},
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    },
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://acemock:acemock@localhost:5432/acemock"

    # LLM: "deepseek" | "gemini" | "groq" | "openai" | "together" | "anthropic".
    # All except anthropic share one OpenAI-compatible code path.
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    # Optional overrides; when blank the provider preset is used.
    llm_base_url: str = ""
    llm_model: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4.5"

    # Embeddings (OpenAI-compatible). text-embedding-3-small is cheap and reliable.
    embedding_api_key: str = ""
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # Voice: ElevenLabs TTS (cheapest at scale) + optional Groq Whisper STT.
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model: str = "eleven_flash_v2_5"
    groq_api_key: str = ""
    groq_stt_model: str = "whisper-large-v3-turbo"

    # Auth (Clerk). When unset, the app runs in dev mode with an anonymous user.
    clerk_secret_key: str = ""
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""

    # Billing (Stripe).
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_quant: str = ""
    billing_success_url: str = "http://localhost:3000/?upgraded=1"
    billing_cancel_url: str = "http://localhost:3000/pricing"

    # Free-tier limits (per calendar month).
    free_monthly_mocks: int = 3

    frontend_origin: str = "http://localhost:3000"

    @property
    def llm_resolved(self) -> dict[str, str]:
        preset = LLM_PRESETS.get(self.llm_provider, LLM_PRESETS["deepseek"])
        return {
            "base_url": self.llm_base_url or preset["base_url"],
            "model": self.llm_model or preset["model"],
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
