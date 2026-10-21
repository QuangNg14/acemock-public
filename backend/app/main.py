import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import behavioral, billing, health, mock, quant, questions, voice
from app.config import get_settings

logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="AceMock API",
    version="0.1.0",
    description="AI mock-interview platform: company-specific banks + mentor-rubric grading.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(questions.router)
app.include_router(mock.router)
app.include_router(behavioral.router)
app.include_router(quant.router)
app.include_router(voice.router)
app.include_router(billing.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "acemock", "docs": "/docs"}
