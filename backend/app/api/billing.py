import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.schemas.dto import BillingMeOut, CheckoutIn, CheckoutOut
from app.services import billing
from app.services.auth import current_user_optional, require_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/me", response_model=BillingMeOut)
async def me(user: User | None = Depends(current_user_optional)) -> BillingMeOut:
    if user is None:
        return BillingMeOut(authenticated=False, is_pro=False)
    return BillingMeOut(authenticated=True, is_pro=user.is_pro, email=user.email)


@router.post("/checkout", response_model=CheckoutOut)
async def checkout(body: CheckoutIn, user: User = Depends(require_user)) -> CheckoutOut:
    if not billing.configured():
        raise HTTPException(status_code=503, detail="billing not configured")
    try:
        return CheckoutOut(url=billing.create_checkout(user, body.plan))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/portal", response_model=CheckoutOut)
async def portal(user: User = Depends(require_user)) -> CheckoutOut:
    if not billing.configured():
        raise HTTPException(status_code=503, detail="billing not configured")
    try:
        return CheckoutOut(url=billing.create_portal(user))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, bool]:
    if not billing.configured():
        raise HTTPException(status_code=503, detail="billing not configured")
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = billing.parse_event(payload, signature)
    except Exception as exc:  # noqa: BLE001 - invalid signature / payload
        logger.warning("Stripe webhook verification failed: %s", exc)
        raise HTTPException(status_code=400, detail="invalid webhook") from exc
    await billing.handle_event(db, event)
    return {"received": True}
