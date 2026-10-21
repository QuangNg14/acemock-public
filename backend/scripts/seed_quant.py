"""Seed a starter set of QuantReady drills across all categories and firm tracks.

Extend this from the vault's quant interview notes over time; this gives the vertical
real content on day one.

Usage:
    python scripts/seed_quant.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db import SessionLocal
from app.models.base import Difficulty, QuantCategory
from app.models.quant import QuantDrill

DRILLS = [
    {
        "category": QuantCategory.probability,
        "difficulty": Difficulty.medium,
        "firm_tracks": "jane-street,optiver,sig",
        "prompt": "You roll two fair six-sided dice. What is the probability that the sum is 7?",
        "answer": "1/6",
        "solution_steps": "6 favorable ordered outcomes out of 36 total = 6/36 = 1/6.",
    },
    {
        "category": QuantCategory.probability,
        "difficulty": Difficulty.hard,
        "firm_tracks": "jane-street,hrt",
        "prompt": "A stick of length 1 is broken at two uniformly random points. What is the probability the three pieces form a triangle?",
        "answer": "1/4",
        "solution_steps": "Each piece must be < 1/2. The favorable region is 1/4 of the unit simplex.",
    },
    {
        "category": QuantCategory.brainteaser,
        "difficulty": Difficulty.medium,
        "firm_tracks": "citadel,two-sigma",
        "prompt": "100 people in a line wear black or white hats and can see all hats in front of them. Going from back to front each guesses their own color; how many can be guaranteed correct?",
        "answer": "99",
        "solution_steps": "The last person encodes the parity of black hats; the other 99 deduce theirs.",
    },
    {
        "category": QuantCategory.mental_math,
        "difficulty": Difficulty.easy,
        "firm_tracks": "optiver,imc,akuna",
        "prompt": "Compute 17 x 23 in your head.",
        "answer": "391",
        "solution_steps": "17 x 23 = 17 x 20 + 17 x 3 = 340 + 51 = 391.",
        "time_limit_seconds": 12,
    },
    {
        "category": QuantCategory.mental_math,
        "difficulty": Difficulty.medium,
        "firm_tracks": "optiver,imc",
        "prompt": "What is 7.5% of 320?",
        "answer": "24",
        "solution_steps": "10% of 320 = 32; 7.5% = 0.75 x 32 = 24.",
        "time_limit_seconds": 10,
    },
    {
        "category": QuantCategory.market_making,
        "difficulty": Difficulty.hard,
        "firm_tracks": "jane-street,optiver,sig",
        "prompt": "A fair coin is flipped 10 times. Make a market on the number of heads (give a bid-ask you would quote).",
        "answer": "5",
        "solution_steps": "Expected value is 5. A tight market would be around 4.5 / 5.5; widen for variance and adverse selection.",
        "time_limit_seconds": 20,
    },
    {
        "category": QuantCategory.probability,
        "difficulty": Difficulty.medium,
        "firm_tracks": "sig,drw",
        "prompt": "Two cards are drawn from a standard 52-card deck without replacement. What is the probability both are aces?",
        "answer": "1/221",
        "solution_steps": "(4/52) x (3/51) = 12/2652 = 1/221.",
    },
    {
        "category": QuantCategory.brainteaser,
        "difficulty": Difficulty.hard,
        "firm_tracks": "jane-street,citadel",
        "prompt": "You have two ropes that each burn in exactly 60 minutes but not uniformly. Measure 45 minutes.",
        "answer": "45",
        "solution_steps": "Light rope A both ends and rope B one end. A finishes at 30 min; then light B's other end, B finishes 15 min later = 45.",
    },
]


async def main() -> None:
    async with SessionLocal() as db:
        existing = set(
            (await db.execute(select(QuantDrill.prompt))).scalars().all()
        )
        added = 0
        for d in DRILLS:
            if d["prompt"] in existing:
                continue
            db.add(QuantDrill(source="pathwise", **d))
            added += 1
        await db.commit()
    print(f"Seeded {added} quant drills.")


if __name__ == "__main__":
    asyncio.run(main())
