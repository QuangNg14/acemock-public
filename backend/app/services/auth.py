"""Clerk authentication via JWKS-verified session tokens.

When Clerk is not configured the app runs in dev mode with a persistent anonymous
user, so every endpoint stays usable locally. Once CLERK_JWKS_URL and CLERK_ISSUER
are set, bearer tokens are cryptographically verified and users are upserted.
"""

import logging

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()

_DEV_CLERK_ID = "dev-anonymous"
_jwks_client = None


def _clerk_configured() -> bool:
    return bool(settings.clerk_jwks_url and settings.clerk_issuer)


def _get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        import jwt

        _jwks_client = jwt.PyJWKClient(settings.clerk_jwks_url)
    return _jwks_client


def _verify_token(token: str) -> dict:
    import jwt

    signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=settings.clerk_issuer,
        options={"verify_aud": False},
    )


async def _upsert_user(db: AsyncSession, clerk_id: str, email: str | None = None) -> User:
    user = (
        await db.execute(select(User).where(User.clerk_id == clerk_id))
    ).scalar_one_or_none()
    if user is None:
        user = User(clerk_id=clerk_id, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def current_user_optional(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not _clerk_configured():
        return await _upsert_user(db, _DEV_CLERK_ID, "dev@acemock.local")
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = _verify_token(token)
    except Exception as exc:  # noqa: BLE001 - any verification failure means unauthenticated
        logger.warning("Clerk token verification failed: %s", exc)
        return None
    return await _upsert_user(db, claims["sub"], claims.get("email"))


async def require_user(user: User | None = Depends(current_user_optional)) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="authentication required")
    return user


async def require_pro(user: User = Depends(require_user)) -> User:
    if not user.is_pro:
        raise HTTPException(status_code=402, detail="Pro subscription required")
    return user
