import json
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.db import get_db
from app.models.base import SessionStatus, Speaker
from app.models.mock_session import MockSession, MockTurn, Scorecard
from app.models.question import Question
from app.models.rubric import Rubric
from app.models.user import User
from app.schemas.dto import (
    MessageIn,
    MockSessionOut,
    ScorecardOut,
    StartMockIn,
    TurnOut,
)
from app.services import grader, interviewer
from app.services.auth import current_user_optional

settings = get_settings()
router = APIRouter(prefix="/mock", tags=["mock"])


async def _enforce_free_limit(db: AsyncSession, user: User | None) -> None:
    if user is None or user.is_pro:
        return
    start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    count = (
        await db.execute(
            select(func.count(MockSession.id)).where(
                MockSession.user_id == user.id, MockSession.created_at >= start
            )
        )
    ).scalar_one()
    if count >= settings.free_monthly_mocks:
        raise HTTPException(
            status_code=402,
            detail="Free monthly mock limit reached. Upgrade to Pro for unlimited mocks.",
        )


async def _load_session(db: AsyncSession, session_id: uuid.UUID) -> MockSession:
    stmt = (
        select(MockSession)
        .where(MockSession.id == session_id)
        .options(selectinload(MockSession.turns), selectinload(MockSession.scorecard))
    )
    session = (await db.execute(stmt)).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


async def _pick_rubric(db: AsyncSession, session: MockSession) -> Rubric | None:
    stmt = (
        select(Rubric)
        .where(Rubric.track == session.track, Rubric.round == session.round)
        .options(selectinload(Rubric.criteria))
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


def _serialize(session: MockSession, question: Question | None) -> MockSessionOut:
    return MockSessionOut(
        id=session.id,
        company=session.company,
        track=session.track,
        round=session.round,
        status=session.status.value,
        hints_used=session.hints_used,
        question=question,  # type: ignore[arg-type]
        turns=[TurnOut.model_validate(t) for t in sorted(session.turns, key=lambda x: x.position)],
    )


@router.post("/start", response_model=MockSessionOut)
async def start_mock(
    body: StartMockIn,
    user: User | None = Depends(current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> MockSessionOut:
    await _enforce_free_limit(db, user)
    if body.question_id:
        question = await db.get(Question, body.question_id)
    else:
        stmt = (
            select(Question)
            .where(Question.company == body.company, Question.track == body.track)
            .order_by(func.random())
            .limit(1)
        )
        question = (await db.execute(stmt)).scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="no question available for that company/track")

    session = MockSession(
        company=body.company,
        track=body.track,
        round=body.round,
        question_id=question.id,
        user_id=user.id if user else None,
    )
    rubric = await _pick_rubric(db, session)
    if rubric:
        session.rubric_id = rubric.id

    opening = interviewer.opening_turn(session, question, rubric)
    session.turns = [
        MockTurn(position=0, speaker=Speaker.interviewer, content=opening, is_hint=False)
    ]
    db.add(session)
    await db.commit()
    return _serialize(session, question)


@router.get("/{session_id}", response_model=MockSessionOut)
async def get_mock(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> MockSessionOut:
    session = await _load_session(db, session_id)
    question = await db.get(Question, session.question_id) if session.question_id else None
    return _serialize(session, question)


@router.post("/{session_id}/message", response_model=MockSessionOut)
async def post_message(
    session_id: uuid.UUID, body: MessageIn, db: AsyncSession = Depends(get_db)
) -> MockSessionOut:
    session = await _load_session(db, session_id)
    if session.status != SessionStatus.active:
        raise HTTPException(status_code=409, detail="session is not active")

    question = await db.get(Question, session.question_id)
    rubric = await _pick_rubric(db, session)
    transcript = sorted(session.turns, key=lambda t: t.position)
    next_pos = len(transcript)

    session.turns.append(
        MockTurn(position=next_pos, speaker=Speaker.candidate, content=body.content, is_hint=False)
    )
    reply, is_hint = interviewer.next_turn(session, question, rubric, transcript, body.content)
    if is_hint:
        session.hints_used += 1
    session.turns.append(
        MockTurn(
            position=next_pos + 1, speaker=Speaker.interviewer, content=reply, is_hint=is_hint
        )
    )
    await db.commit()
    return _serialize(session, question)


@router.post("/{session_id}/grade", response_model=ScorecardOut)
async def grade_mock(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ScorecardOut:
    session = await _load_session(db, session_id)
    rubric = await _pick_rubric(db, session)
    if rubric is None:
        raise HTTPException(status_code=400, detail="no rubric configured for this track/round")

    transcript = sorted(session.turns, key=lambda t: t.position)
    result = grader.grade(rubric, transcript, session.hints_used)

    card = session.scorecard or Scorecard(session_id=session.id)
    card.overall = result["overall"]
    card.recommendation = result["recommendation"]
    card.breakdown = result["breakdown"]
    card.strengths = result.get("strengths")
    card.improvements = result.get("improvements")
    session.scorecard = card
    session.status = SessionStatus.graded
    await db.commit()

    return ScorecardOut(
        overall=card.overall,
        recommendation=card.recommendation,
        breakdown=json.loads(card.breakdown),
        strengths=card.strengths,
        improvements=card.improvements,
    )
