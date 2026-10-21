import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.base import Track
from app.models.question import Question
from app.models.user import User
from app.schemas.dto import QuestionOut, SolutionOut
from app.services.auth import require_pro

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/companies")
async def list_companies(db: AsyncSession = Depends(get_db)) -> list[dict]:
    stmt = (
        select(Question.company, func.count(Question.id))
        .group_by(Question.company)
        .order_by(func.count(Question.id).desc())
    )
    rows = (await db.execute(stmt)).all()
    return [{"company": c, "count": n} for c, n in rows]


@router.get("", response_model=list[QuestionOut])
async def list_questions(
    company: str | None = None,
    track: Track | None = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[Question]:
    stmt = select(Question)
    if company:
        stmt = stmt.where(Question.company == company)
    if track:
        stmt = stmt.where(Question.track == track)
    stmt = stmt.limit(limit).offset(offset)
    return list((await db.execute(stmt)).scalars().all())


@router.get("/tracks")
async def list_tracks(db: AsyncSession = Depends(get_db)) -> list[str]:
    rows = (await db.execute(select(distinct(Question.track)))).scalars().all()
    return [t.value for t in rows]


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(question_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Question:
    q = await db.get(Question, question_id)
    if q is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="question not found")
    return q


@router.get("/{question_id}/solution", response_model=SolutionOut)
async def get_solution(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_pro),
) -> SolutionOut:
    q = await db.get(Question, question_id)
    if q is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="question not found")
    return SolutionOut(solution=q.solution)
