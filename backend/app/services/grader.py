"""Grader service: rubric-calibrated scoring of a finished session."""

import json
import logging
from typing import Any

from app.ai.prompts.grader import grader_system_prompt, grader_user_prompt
from app.models.mock_session import MockTurn
from app.models.rubric import Rubric
from app.services import llm

logger = logging.getLogger(__name__)

_RECOMMENDATIONS = {"strong_no", "no", "lean_no", "lean_yes", "yes"}


def _criteria_payload(rubric: Rubric) -> list[dict[str, Any]]:
    return [
        {
            "name": c.name,
            "description": c.description,
            "weight": c.weight,
            "anchor_1": c.anchor_1,
            "anchor_3": c.anchor_3,
            "anchor_5": c.anchor_5,
        }
        for c in rubric.criteria
    ]


def grade(rubric: Rubric, transcript: list[MockTurn], hints_used: int) -> dict[str, Any]:
    criteria = _criteria_payload(rubric)
    convo = [{"speaker": t.speaker.value, "content": t.content} for t in transcript]
    result = llm.complete_json(
        system=grader_system_prompt(),
        user=grader_user_prompt(criteria, convo, hints_used),
        max_tokens=1100,
    )
    return _normalize(result, criteria)


def _normalize(result: dict[str, Any], criteria: list[dict[str, Any]]) -> dict[str, Any]:
    """Recompute the weighted overall from the breakdown so it is internally consistent."""
    breakdown = result.get("breakdown") or []
    if breakdown:
        total_w = sum(float(b.get("weight", 1.0)) for b in breakdown) or 1.0
        weighted = sum(float(b.get("score", 0)) * float(b.get("weight", 1.0)) for b in breakdown)
        result["overall"] = round(weighted / total_w, 2)
    rec = result.get("recommendation", "lean_no")
    if rec not in _RECOMMENDATIONS:
        result["recommendation"] = _bucket(result.get("overall", 0.0))
    result["breakdown"] = json.dumps(breakdown)
    return result


def _bucket(overall: float) -> str:
    if overall >= 4.3:
        return "yes"
    if overall >= 3.5:
        return "lean_yes"
    if overall >= 2.8:
        return "lean_no"
    if overall >= 2.0:
        return "no"
    return "strong_no"
