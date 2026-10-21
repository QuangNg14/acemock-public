"""Seed the question banks from the Pathwise Obsidian vault.

Reads the two source folders (Online Assessments and Company Interviews), derives
company / track / round from each note, and inserts one Question per note. This is
the data moat: real, company-specific questions.

Usage:
    python scripts/seed_vault.py --vault "/path/to/your-vault" --limit 300
"""

import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db import SessionLocal
from app.models.base import Round, Track
from app.models.question import Question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_vault")

OA_SUBPATH = Path("Pathwise Resources/03-Online-Assessments/All Shared Online Assessments (OA)")
INT_SUBPATH = Path("Pathwise Resources/06-Company-Interviews")

QUANT_FIRMS = {
    "jane street", "citadel", "optiver", "hrt", "sig", "two sigma", "imc", "drw",
    "akuna", "belvedere", "marshall wace", "millenium", "millennium", "point72",
    "voleon", "walleye", "jump", "jefferies", "blackrock", "blackstone",
}

_TRAILERS = re.compile(
    r"\b(oa|online assessment|interview|final|round|hirevue|superday|phone|vo|"
    r"updated|part|notes|questions|prep|bank)\b.*$",
    re.IGNORECASE,
)


def normalize_company(filename: str) -> str:
    name = filename.replace(".md", "")
    name = re.sub(r"[-+_].*$", "", name)  # drop suffixes after first separator
    name = _TRAILERS.sub("", name)
    name = re.sub(r"\s+\d.*$", "", name)  # drop trailing dates/numbers
    return name.strip(" -+_") or filename.replace(".md", "")


def detect_track(filename: str, company: str) -> Track:
    low = (filename + " " + company).lower()
    if company.lower() in QUANT_FIRMS or "quant" in low or "trading" in low:
        return Track.quant
    if re.search(r"\b(ds|de|da|data|analytics|mle|ml)\b", low):
        return Track.data
    return Track.swe


def detect_round(filename: str, is_oa: bool) -> Round:
    low = filename.lower()
    if is_oa or "oa" in low or "hirevue" in low:
        return Round.oa
    if "system design" in low or "design" in low:
        return Round.system_design
    if "behavioral" in low:
        return Round.behavioral
    if "phone" in low:
        return Round.phone
    return Round.onsite


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].lstrip()
    return text


def build_prompt(body: str, max_chars: int = 6000) -> str:
    body = strip_frontmatter(body).strip()
    return body[:max_chars]


async def seed_dir(db, base: Path, is_oa: bool, limit: int, seen: set[str]) -> int:
    if not base.exists():
        logger.warning("Missing source dir: %s", base)
        return 0
    count = 0
    for md in sorted(base.rglob("*.md")):
        if count >= limit:
            break
        if md.name.startswith("_"):
            continue
        ref = str(md.relative_to(base.parents[2])) if len(md.parents) > 2 else md.name
        if ref in seen:
            continue
        try:
            body = md.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logger.warning("Cannot read %s: %s", md, exc)
            continue
        prompt = build_prompt(body)
        if len(prompt) < 40:
            continue
        company = normalize_company(md.name)
        track = detect_track(md.name, company)
        round_ = detect_round(md.name, is_oa)
        db.add(
            Question(
                company=company,
                track=track,
                round=round_,
                title=md.stem,
                prompt=prompt,
                source="pathwise",
                source_ref=ref,
            )
        )
        seen.add(ref)
        count += 1
    return count


async def main(vault: Path, limit: int) -> None:
    async with SessionLocal() as db:
        existing = (await db.execute(select(Question.source_ref))).scalars().all()
        seen = {r for r in existing if r}
        oa = await seed_dir(db, vault / OA_SUBPATH, True, limit, seen)
        intv = await seed_dir(db, vault / INT_SUBPATH, False, limit, seen)
        await db.commit()
    logger.info("Seeded %d OA + %d interview questions (deduped).", oa, intv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Path to the Pathwise vault root")
    parser.add_argument("--limit", type=int, default=300, help="Max notes per source dir")
    args = parser.parse_args()
    asyncio.run(main(Path(args.vault), args.limit))
