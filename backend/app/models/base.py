import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class Track(str, enum.Enum):
    swe = "swe"
    data = "data"
    quant = "quant"


class Round(str, enum.Enum):
    oa = "oa"
    phone = "phone"
    coding = "coding"
    system_design = "system_design"
    behavioral = "behavioral"
    onsite = "onsite"


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuantCategory(str, enum.Enum):
    brainteaser = "brainteaser"
    probability = "probability"
    mental_math = "mental_math"
    market_making = "market_making"


class SessionStatus(str, enum.Enum):
    active = "active"
    graded = "graded"
    abandoned = "abandoned"


class Speaker(str, enum.Enum):
    interviewer = "interviewer"
    candidate = "candidate"
