"""Create all tables directly (fast path for local dev without Alembic).

For production use `alembic upgrade head` instead. This helper is convenient for
spinning up a throwaway database or running the seed scripts in CI.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.db import engine
from app.models import Base


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Schema created.")


if __name__ == "__main__":
    asyncio.run(main())
