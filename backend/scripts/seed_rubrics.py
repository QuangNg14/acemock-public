"""Seed the mentor-calibrated rubrics. The grader always grades against these.

Run after the schema exists:
    python scripts/seed_rubrics.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db import SessionLocal
from app.models.base import Round, Track
from app.models.rubric import Rubric, RubricCriterion

CODING_HINTS = [
    "Restate the problem and confirm input/output and constraints.",
    "What brute-force solution works? State its time and space complexity.",
    "Which data structure removes the bottleneck in the brute force?",
    "Consider a hashmap / two-pointer / sliding-window reframe of the inner loop.",
    "Walk one concrete example through your proposed structure step by step.",
    "State the optimal complexity target and code toward it.",
]

SYS_HINTS = [
    "Clarify functional requirements and the read/write scale (QPS, data size).",
    "Sketch the high-level components before any single deep dive.",
    "Where is the bottleneck: storage, read path, or write path?",
    "Introduce caching / a CDN / a queue at the contended layer.",
    "How do you shard or partition the hot data store?",
    "Address consistency, failure modes, and back-pressure explicitly.",
]

BEHAVIORAL_HINTS = [
    "Anchor the story: one specific situation, not a general pattern.",
    "What was YOUR task and ownership, distinct from the team's?",
    "Detail the specific actions you personally took.",
    "Quantify the result with a metric or concrete outcome.",
]

RUBRICS = [
    {
        "name": "SWE Coding Interview (mentor calibrated)",
        "track": Track.swe,
        "round": Round.coding,
        "hint_ladder": CODING_HINTS,
        "criteria": [
            ("Problem Solving", "Reaches a correct, optimal approach with sound reasoning.", 3.0,
             "Stuck without progress even with hints.",
             "Reaches a working solution after a hint or two.",
             "Independently reaches the optimal approach and justifies it."),
            ("Coding", "Translates the approach into clean, bug-free code.", 2.5,
             "Code does not run or has major logic errors.",
             "Mostly correct with minor bugs caught on review.",
             "Clean, idiomatic, correct on the first pass."),
            ("Communication", "Thinks aloud, takes input, explains trade-offs.", 2.0,
             "Silent or unclear; hard to follow.",
             "Explains most steps; some prompting needed.",
             "Crisp narration; collaborates and justifies choices."),
            ("Testing & Edge Cases", "Proactively tests and handles edge cases.", 1.5,
             "No testing; misses obvious edge cases.",
             "Tests the happy path and a couple of edges.",
             "Systematically enumerates and handles edge cases."),
        ],
    },
    {
        "name": "System Design Interview (mentor calibrated)",
        "track": Track.swe,
        "round": Round.system_design,
        "hint_ladder": SYS_HINTS,
        "criteria": [
            ("Requirements & Scope", "Clarifies functional and non-functional requirements and scale.", 2.5,
             "Jumps to a solution with no scoping.",
             "Captures core requirements and rough scale.",
             "Drives scope, estimates QPS/storage, sets priorities."),
            ("High-Level Design", "Proposes a coherent, justified component architecture.", 3.0,
             "Incoherent or missing major components.",
             "Reasonable architecture with some gaps.",
             "Clean architecture with justified trade-offs."),
            ("Deep Dive", "Goes deep on the bottleneck with concrete mechanisms.", 2.5,
             "Stays shallow; no real bottleneck analysis.",
             "Identifies a bottleneck and a plausible fix.",
             "Rigorous deep dive: sharding, caching, consistency."),
            ("Trade-offs & Failure", "Reasons about CAP, failure modes, scaling limits.", 2.0,
             "Ignores failure and trade-offs.",
             "Mentions trade-offs when prompted.",
             "Proactively reasons about consistency and failures."),
        ],
    },
    {
        "name": "Behavioral Interview (mentor calibrated)",
        "track": Track.swe,
        "round": Round.behavioral,
        "hint_ladder": BEHAVIORAL_HINTS,
        "criteria": [
            ("Structure (STAR)", "Clear situation, task, action, result with no rambling.", 2.5,
             "No structure; meandering answer.",
             "Recognizable STAR with some drift.",
             "Tight STAR; easy to follow and complete."),
            ("Specificity & Ownership", "Concrete, first-person actions and metrics.", 3.0,
             "Vague 'we' language; no metrics.",
             "Some specifics; partial ownership.",
             "Clear personal ownership with quantified impact."),
            ("Value Alignment", "Story evidences the probed company value/LP.", 2.5,
             "Story does not fit the value.",
             "Loosely fits the value.",
             "Directly and convincingly evidences the value."),
            ("Reflection", "Shows learning and what they'd do differently.", 1.5,
             "No reflection.",
             "Brief lesson learned.",
             "Insightful reflection and growth."),
        ],
    },
]


async def main() -> None:
    async with SessionLocal() as db:
        for r in RUBRICS:
            exists = (
                await db.execute(select(Rubric).where(Rubric.name == r["name"]))
            ).scalar_one_or_none()
            if exists:
                continue
            rubric = Rubric(
                name=r["name"],
                track=r["track"],
                round=r["round"],
                hint_ladder=json.dumps(r["hint_ladder"]),
            )
            for i, (name, desc, weight, a1, a3, a5) in enumerate(r["criteria"]):
                rubric.criteria.append(
                    RubricCriterion(
                        position=i,
                        name=name,
                        description=desc,
                        weight=weight,
                        anchor_1=a1,
                        anchor_3=a3,
                        anchor_5=a5,
                    )
                )
            db.add(rubric)
        await db.commit()
    print(f"Seeded {len(RUBRICS)} rubrics.")


if __name__ == "__main__":
    asyncio.run(main())
