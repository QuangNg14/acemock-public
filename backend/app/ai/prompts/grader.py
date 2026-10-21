"""Prompt builder for the rubric grader.

The grader never free-scores. It receives the rubric criteria with anchored levels
and the full transcript, and must return a calibrated 1-5 per criterion plus an
overall weighted score and a hire recommendation.
"""

import json
from typing import Any


def grader_system_prompt() -> str:
    return (
        "You are a calibrated interview grader. You score strictly against the provided "
        "rubric criteria and their anchored levels (1, 3, 5). You never invent criteria. "
        "You justify every score with a specific quote or moment from the transcript. "
        "You return only valid JSON."
    )


def grader_user_prompt(
    criteria: list[dict[str, Any]],
    transcript: list[dict[str, str]],
    hints_used: int,
) -> str:
    crit_lines = []
    for c in criteria:
        crit_lines.append(
            f"- {c['name']} (weight {c['weight']}): {c['description']}\n"
            f"    anchor 1: {c.get('anchor_1', 'n/a')}\n"
            f"    anchor 3: {c.get('anchor_3', 'n/a')}\n"
            f"    anchor 5: {c.get('anchor_5', 'n/a')}"
        )
    crit_block = "\n".join(crit_lines)
    convo = "\n".join(f"[{t['speaker']}] {t['content']}" for t in transcript)

    schema = {
        "overall": "float 1-5 (weighted average)",
        "recommendation": "one of strong_no|no|lean_no|lean_yes|yes",
        "breakdown": [
            {"criterion": "str", "score": "float 1-5", "weight": "float", "justification": "str"}
        ],
        "strengths": "str",
        "improvements": "str",
    }

    return (
        f"RUBRIC CRITERIA:\n{crit_block}\n\n"
        f"HINTS USED BY CANDIDATE: {hints_used} (more hints should lower the relevant scores)\n\n"
        f"TRANSCRIPT:\n{convo}\n\n"
        f"Return JSON matching exactly this schema:\n{json.dumps(schema, indent=2)}"
    )
