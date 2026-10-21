from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StripeEvent(Base):
    """Processed Stripe webhook events, for idempotent entitlement grants."""

    __tablename__ = "stripe_events"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)  # Stripe event id
    type: Mapped[str] = mapped_column(String(120))
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
