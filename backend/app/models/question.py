import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.config import get_settings
from app.models.base import Base, Difficulty, Round, TimestampMixin, Track, uuid_pk

_dim = get_settings().embedding_dim


class Question(Base, TimestampMixin):
    """A real interview or OA question seeded from the vault banks."""

    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = uuid_pk()
    company: Mapped[str] = mapped_column(String(120), index=True)
    role_category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    track: Mapped[Track] = mapped_column(SAEnum(Track, name="track"), index=True)
    round: Mapped[Round] = mapped_column(SAEnum(Round, name="round"), index=True)
    difficulty: Mapped[Difficulty | None] = mapped_column(
        SAEnum(Difficulty, name="difficulty"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(300))
    prompt: Mapped[str] = mapped_column(Text)
    # Pro-gated: never returned for locked questions through the public API.
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    topics: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated tags
    leetcode_number: Mapped[int | None] = mapped_column(nullable=True)

    source: Mapped[str] = mapped_column(String(60), default="pathwise")
    source_ref: Mapped[str | None] = mapped_column(String(400), nullable=True)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(_dim), nullable=True)

    __table_args__ = (
        Index("ix_questions_company_track", "company", "track"),
    )
