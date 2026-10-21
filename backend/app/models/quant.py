import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Difficulty, QuantCategory, TimestampMixin, uuid_pk


class QuantDrill(Base, TimestampMixin):
    """A quant-prep item: brainteaser, probability, mental-math, or market-making."""

    __tablename__ = "quant_drills"

    id: Mapped[uuid.UUID] = uuid_pk()
    category: Mapped[QuantCategory] = mapped_column(
        SAEnum(QuantCategory, name="quant_category"), index=True
    )
    difficulty: Mapped[Difficulty] = mapped_column(SAEnum(Difficulty, name="difficulty"))
    # Firm tracks this drill is representative of, e.g. "jane-street,optiver".
    firm_tracks: Mapped[str | None] = mapped_column(String(300), nullable=True, index=True)

    prompt: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)  # Pro-gated
    solution_steps: Mapped[str | None] = mapped_column(Text, nullable=True)  # Pro-gated
    # For mental-math/market-making timed modes.
    time_limit_seconds: Mapped[int | None] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(String(60), default="pathwise")

    attempts: Mapped[list["QuantAttempt"]] = relationship(
        back_populates="drill", cascade="all, delete-orphan"
    )


class QuantAttempt(Base, TimestampMixin):
    __tablename__ = "quant_attempts"

    id: Mapped[uuid.UUID] = uuid_pk()
    drill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quant_drills.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct: Mapped[bool] = mapped_column(Boolean, default=False)
    elapsed_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    drill: Mapped[QuantDrill] = relationship(back_populates="attempts")
