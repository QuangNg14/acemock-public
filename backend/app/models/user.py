import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class User(Base, TimestampMixin):
    """Minimal user record. Identity is owned by Clerk; this mirrors entitlement."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    clerk_id: Mapped[str | None] = mapped_column(
        String(120), unique=True, nullable=True, index=True
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_pro: Mapped[bool] = mapped_column(Boolean, default=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
