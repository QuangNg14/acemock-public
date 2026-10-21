import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk


class BehavioralStory(Base, TimestampMixin):
    """A candidate STAR story mapped to company values / leadership principles."""

    __tablename__ = "behavioral_stories"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    situation: Mapped[str] = mapped_column(Text)
    task: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    result: Mapped[str] = mapped_column(Text)
    # JSON arrays of mapped values, e.g. Amazon LPs this story evidences.
    mapped_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_companies: Mapped[str | None] = mapped_column(Text, nullable=True)

    drills: Mapped[list["BehavioralDrill"]] = relationship(
        back_populates="story", cascade="all, delete-orphan"
    )


class BehavioralDrill(Base, TimestampMixin):
    """A graded practice round of a story against a behavioral rubric."""

    __tablename__ = "behavioral_drills"

    id: Mapped[uuid.UUID] = uuid_pk()
    story_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("behavioral_stories.id", ondelete="CASCADE"), index=True
    )
    company: Mapped[str | None] = mapped_column(String(120), nullable=True)
    value_probed: Mapped[str | None] = mapped_column(String(160), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    structure_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    specificity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    followups: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    story: Mapped[BehavioralStory] = relationship(back_populates="drills")
