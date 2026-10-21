import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.prompts.quant_coach import quant_grader_prompt
from app.db import get_db
from app.models.base import QuantCategory
from app.models.quant import QuantAttempt, QuantDrill
from app.models.user import User
from app.schemas.dto import QuantAttemptIn, QuantAttemptOut, QuantDrillOut, SolutionOut
from app.services import llm
from app.services.auth import current_user_optional, require_pro

router = APIRouter(prefix="/quant", tags=["quant"])


@router.get("/drills", response_model=list[QuantDrillOut])
async def list_drills(
    category: QuantCategory | None = None,
    firm: str | None = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[QuantDrill]:
    stmt = select(QuantDrill)
    if category:
        stmt = stmt.where(QuantDrill.category == category)
    if firm:
        stmt = stmt.where(QuantDrill.firm_tracks.ilike(f"%{firm}%"))
    stmt = stmt.order_by(func.random()).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


@router.get("/drills/{drill_id}/solution", response_model=SolutionOut)
async def get_drill_solution(
    drill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_pro),
) -> SolutionOut:
    drill = await db.get(QuantDrill, drill_id)
    if drill is None:
        raise HTTPException(status_code=404, detail="drill not found")
    return SolutionOut(answer=drill.answer, solution_steps=drill.solution_steps)


@router.post("/attempts", response_model=QuantAttemptOut)
async def submit_attempt(
    body: QuantAttemptIn,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> QuantAttemptOut:
    drill = await db.get(QuantDrill, body.drill_id)
    if drill is None:
        raise HTTPException(status_code=404, detail="drill not found")

    reference = (drill.answer or "").strip()
    deterministic = _exact_match(reference, body.response)
    if deterministic is not None:
        correct, feedback, quality = deterministic, _det_feedback(deterministic), None
    else:
        result = llm.complete_json(
            system="You grade quant interview answers. Return only JSON.",
            user=quant_grader_prompt(drill.category.value, drill.prompt, reference, body.response),
        )
        correct = bool(result.get("correct", False))
        feedback = result.get("feedback")
        quality = result.get("reasoning_quality")

    db.add(
        QuantAttempt(
            drill_id=drill.id,
            user_id=user.id if user else None,
            response=body.response,
            correct=correct,
            elapsed_seconds=body.elapsed_seconds,
            feedback=feedback,
        )
    )
    await db.commit()
    return QuantAttemptOut(correct=correct, feedback=feedback, reasoning_quality=quality)


def _exact_match(reference: str, response: str) -> bool | None:
    """Deterministic check for numeric answers; returns None when not numeric.

    Integer answers require exact equality (mental-math must be exact); non-integer
    answers (fractions, probabilities) allow a small tolerance for rounding.
    """
    ref_num = _to_number(reference)
    resp_num = _to_number(response)
    if ref_num is None or resp_num is None:
        return None
    if _is_integer(ref_num):
        return _is_integer(resp_num) and int(round(ref_num)) == int(round(resp_num))
    tol = max(1e-4, abs(ref_num) * 0.01)
    return abs(ref_num - resp_num) <= tol


def _is_integer(value: float) -> bool:
    return abs(value - round(value)) < 1e-9


def _to_number(text: str) -> float | None:
    cleaned = text.strip().replace("%", "").replace(",", "").replace("$", "")
    if "/" in cleaned:
        parts = cleaned.split("/")
        if len(parts) == 2:
            try:
                return float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _det_feedback(correct: bool) -> str:
    return "Correct." if correct else "Final answer does not match. Recheck your arithmetic."
