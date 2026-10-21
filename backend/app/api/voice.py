import io

from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas.dto import TTSIn
from app.services import voice

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/status")
def status() -> dict[str, bool]:
    return {"tts": voice.tts_available(), "stt": voice.stt_available()}


@router.post("/tts")
def tts(body: TTSIn):
    if not voice.tts_available():
        raise HTTPException(status_code=503, detail="TTS not configured; use browser fallback")
    audio = voice.synthesize(body.text)
    from fastapi.responses import StreamingResponse

    return StreamingResponse(io.BytesIO(audio), media_type="audio/mpeg")


@router.post("/stt")
async def stt(file: UploadFile) -> dict[str, str]:
    if not voice.stt_available():
        raise HTTPException(status_code=503, detail="STT not configured; use browser fallback")
    audio = await file.read()
    text = voice.transcribe(audio, file.filename or "audio.webm")
    return {"text": text}
