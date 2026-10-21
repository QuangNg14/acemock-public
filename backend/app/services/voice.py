"""Cost-optimized voice: ElevenLabs Flash TTS + optional Groq Whisper STT.

Both are configured by env keys. When a key is missing the corresponding endpoint
returns 503 and the frontend falls back to the free browser Web Speech / speechSynthesis
APIs, so voice mode degrades gracefully instead of breaking.
"""

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_TTS_TIMEOUT = 30
_STT_TIMEOUT = 60


def tts_available() -> bool:
    return bool(settings.elevenlabs_api_key)


def stt_available() -> bool:
    return bool(settings.groq_api_key)


def synthesize(text: str) -> bytes:
    """Return MP3 audio for text via ElevenLabs Flash (cheapest at scale)."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    resp = httpx.post(
        url,
        headers={
            "xi-api-key": settings.elevenlabs_api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        },
        json={
            "text": text,
            "model_id": settings.elevenlabs_model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
        timeout=_TTS_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.content


def transcribe(audio: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio via Groq Whisper ($0.02/hr, the cheapest hosted STT)."""
    resp = httpx.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers={"authorization": f"Bearer {settings.groq_api_key}"},
        files={"file": (filename, audio)},
        data={"model": settings.groq_stt_model, "response_format": "json"},
        timeout=_STT_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("text", "")
