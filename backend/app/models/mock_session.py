import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    Round,
    SessionStatus,
    Speaker,
    TimestampMixin,
    Track,
    uuid_pk,
)


class MockSession(Base, TimestampMixin):
    """One live mock interview: a target company/role, its turns, and a graded scorecard."""

    __tablename__ = "mock_sessions"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    company: Mapped[str] = mapped_column(String(120), index=True)
    track: Mapped[Track] = mapped_column(SAEnum(Track, name="track"))
    round: Mapped[Round] = mapped_column(SAEnum(Round, name="round"))
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )
    rubric_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rubrics.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[SessionStatus] = mapped_column(
        SAEnum(SessionStatus, name="session_status"), default=SessionStatus.active
    )
    hints_used: Mapped[int] = mapped_column(Integer, default=0)

    turns: Mapped[list["MockTurn"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="MockTurn.position"
    )
    scorecard: Mapped["Scorecard | None"] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=False
    )


class MockTurn(Base, TimestampMixin):
    """A single utterance in the interview transcript."""

    __tablename__ = "mock_turns"

    id: Mapped[uuid.UUID] = uuid_pk()
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mock_sessions.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    speaker: Mapped[Speaker] = mapped_column(SAEnum(Speaker, name="speaker"))
    content: Mapped[str] = mapped_column(Text)
    # True when the interviewer turn dispensed a hint-ladder rung.
    is_hint: Mapped[bool] = mapped_column(default=False)

    session: Mapped[MockSession] = relationship(back_populates="turns")


class Scorecard(Base, TimestampMixin):
    """Rubric-graded result for a finished session."""

    __tablename__ = "scorecards"

    id: Mapped[uuid.UUID] = uuid_pk()
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mock_sessions.id", ondelete="CASCADE"), unique=True, index=True
    )
    overall: Mapped[float] = mapped_column(Float)  # weighted 1-5
    recommendation: Mapped[str] = mapped_column(String(40))  # strong_no/no/lean_no/lean_yes/yes
    # JSON: [{criterion, score, weight, justification}]
    breakdown: Mapped[str] = mapped_column(Text)
    strengths: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvements: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped[MockSession] = relationship(back_populates="scorecard")
