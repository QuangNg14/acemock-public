import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.config import get_settings
from app.models import Base  # noqa: F401  (registers all model metadata)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    raise SystemExit("Offline migrations are not supported for this async setup.")
run_migrations_online()
