import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Round, TimestampMixin, Track, uuid_pk


class Rubric(Base, TimestampMixin):
    """A mentor-calibrated scoring key. The grader always grades against one of these."""

    __tablename__ = "rubrics"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(160))
    track: Mapped[Track] = mapped_column(SAEnum(Track, name="track"), index=True)
    round: Mapped[Round] = mapped_column(SAEnum(Round, name="round"), index=True)
    # Ordered hint ladder applied when a candidate stalls (least -> most revealing).
    hint_ladder: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of strings

    criteria: Mapped[list["RubricCriterion"]] = relationship(
        back_populates="rubric", cascade="all, delete-orphan", order_by="RubricCriterion.position"
    )


class RubricCriterion(Base):
    """One weighted dimension of a rubric (e.g. 'Communication', 'Correctness')."""

    __tablename__ = "rubric_criteria"

    id: Mapped[uuid.UUID] = uuid_pk()
    rubric_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rubrics.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    # Anchored descriptions so scores are calibrated, not free-form.
    anchor_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    anchor_3: Mapped[str | None] = mapped_column(Text, nullable=True)
    anchor_5: Mapped[str | None] = mapped_column(Text, nullable=True)

    rubric: Mapped[Rubric] = relationship(back_populates="criteria")
