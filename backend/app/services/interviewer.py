"""Interviewer service: turn management for a live mock session."""

import json
import logging

from app.ai.prompts.interviewer import interviewer_system_prompt, opening_turn_prompt
from app.models.mock_session import MockSession, MockTurn
from app.models.question import Question
from app.models.rubric import Rubric
from app.services import llm

logger = logging.getLogger(__name__)


def _hint_ladder(rubric: Rubric | None) -> list[str]:
    if rubric and rubric.hint_ladder:
        try:
            return json.loads(rubric.hint_ladder)
        except json.JSONDecodeError:
            logger.warning("Malformed hint_ladder on rubric %s", rubric.id)
    return []


def _system(session: MockSession, question: Question, rubric: Rubric | None) -> str:
    return interviewer_system_prompt(
        company=session.company,
        track=session.track.value,
        round_name=session.round.value,
        question_title=question.title,
        question_prompt=question.prompt,
        hint_ladder=_hint_ladder(rubric),
    )


def opening_turn(session: MockSession, question: Question, rubric: Rubric | None) -> str:
    return llm.complete(
        system=_system(session, question, rubric),
        user=opening_turn_prompt(session.company),
        max_tokens=300,
    )


def next_turn(
    session: MockSession,
    question: Question,
    rubric: Rubric | None,
    transcript: list[MockTurn],
    candidate_message: str,
) -> tuple[str, bool]:
    """Produce the interviewer's next turn. Returns (text, is_hint).

    A hint is released when the candidate has stalled on the two most recent
    candidate turns (short, low-progress messages).
    """
    is_hint = _should_hint(transcript, candidate_message)
    history = "\n".join(f"[{t.speaker.value}] {t.content}" for t in transcript)
    directive = (
        "The candidate is stuck. Release ONLY the next unused rung of the hint ladder, "
        "phrased as a natural nudge."
        if is_hint
        else "Continue the interview: probe, challenge an assumption, or move to the next sub-step."
    )
    user = f"TRANSCRIPT SO FAR:\n{history}\n\n[candidate] {candidate_message}\n\n{directive}"
    text = llm.complete(system=_system(session, question, rubric), user=user, max_tokens=260)
    return text, is_hint


def _should_hint(transcript: list[MockTurn], candidate_message: str) -> bool:
    recent_candidate = [t for t in transcript if t.speaker.value == "candidate"][-1:]
    stalled_now = len(candidate_message.split()) < 12
    stalled_prev = bool(recent_candidate) and len(recent_candidate[-1].content.split()) < 12
    return stalled_now and stalled_prev
