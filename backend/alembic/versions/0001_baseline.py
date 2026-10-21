"""baseline schema

Revision ID: 0001
Revises:
Create Date: 2026-06-12
"""

from alembic import op
from app.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector must exist before the vector-typed columns are created.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    # Approximate-nearest-neighbour index for semantic question retrieval.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_questions_embedding "
        "ON questions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS ix_questions_embedding")
    Base.metadata.drop_all(bind=bind)
