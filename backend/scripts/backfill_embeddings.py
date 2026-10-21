"""Backfill embeddings for questions that do not have one yet.

Cheap and resumable: embeds in batches and commits as it goes. No-op without an
embedding API key.

Usage:
    python scripts/backfill_embeddings.py --batch 64
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db import SessionLocal
from app.models.question import Question
from app.services import embeddings


async def main(batch: int) -> None:
    async with SessionLocal() as db:
        stmt = select(Question).where(Question.embedding.is_(None))
        rows = list((await db.execute(stmt)).scalars().all())
        if not rows:
            print("Nothing to embed.")
            return
        done = 0
        for i in range(0, len(rows), batch):
            chunk = rows[i : i + batch]
            texts = [f"{q.company} {q.title}\n{q.prompt[:2000]}" for q in chunk]
            vectors = embeddings.embed_texts(texts)
            if vectors is None:
                print("No embedding API key configured; aborting.")
                return
            for q, vec in zip(chunk, vectors, strict=True):
                q.embedding = vec
            await db.commit()
            done += len(chunk)
            print(f"Embedded {done}/{len(rows)}")
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=64)
    args = parser.parse_args()
    asyncio.run(main(args.batch))
