"""Stripe billing: checkout, customer portal, and idempotent webhook handling."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.stripe_event import StripeEvent
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

PLAN_PRICES = {
    "pro": lambda: settings.stripe_price_pro,
    "quant": lambda: settings.stripe_price_quant,
}


def configured() -> bool:
    return bool(settings.stripe_secret_key)


def _client():
    import stripe

    stripe.api_key = settings.stripe_secret_key
    return stripe


def create_checkout(user: User, plan: str) -> str:
    price_id = PLAN_PRICES.get(plan, PLAN_PRICES["pro"])()
    if not price_id:
        raise ValueError(f"No Stripe price configured for plan '{plan}'")
    stripe = _client()
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        client_reference_id=str(user.id),
        customer=user.stripe_customer_id or None,
        customer_email=None if user.stripe_customer_id else user.email,
        success_url=settings.billing_success_url,
        cancel_url=settings.billing_cancel_url,
        metadata={"user_id": str(user.id), "plan": plan},
    )
    return session.url


def create_portal(user: User) -> str:
    if not user.stripe_customer_id:
        raise ValueError("user has no Stripe customer")
    stripe = _client()
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=settings.frontend_origin,
    )
    return session.url


def parse_event(payload: bytes, signature: str):
    stripe = _client()
    return stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)


async def handle_event(db: AsyncSession, event: dict) -> None:
    """Apply an entitlement change exactly once per Stripe event id."""
    event_id = event["id"]
    already = await db.get(StripeEvent, event_id)
    if already is not None:
        return

    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _grant(db, obj.get("client_reference_id"), obj.get("customer"), is_pro=True)
    elif event_type in {"customer.subscription.updated", "customer.subscription.created"}:
        active = obj.get("status") in {"active", "trialing"}
        await _grant_by_customer(db, obj.get("customer"), is_pro=active)
    elif event_type == "customer.subscription.deleted":
        await _grant_by_customer(db, obj.get("customer"), is_pro=False)

    db.add(StripeEvent(id=event_id, type=event_type))
    await db.commit()


async def _grant(db: AsyncSession, user_id: str | None, customer: str | None, is_pro: bool) -> None:
    if not user_id:
        return
    import uuid

    user = await db.get(User, uuid.UUID(user_id))
    if user is None:
        return
    user.is_pro = is_pro
    if customer:
        user.stripe_customer_id = customer


async def _grant_by_customer(db: AsyncSession, customer: str | None, is_pro: bool) -> None:
    if not customer:
        return
    user = (
        await db.execute(select(User).where(User.stripe_customer_id == customer))
    ).scalar_one_or_none()
    if user is not None:
        user.is_pro = is_pro
