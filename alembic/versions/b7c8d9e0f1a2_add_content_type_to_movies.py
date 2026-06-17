"""add content_type to movies

Revision ID: b7c8d9e0f1a2
Revises: 159c44f3d12f
Create Date: 2026-06-17 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "159c44f3d12f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "movies",
        sa.Column("content_type", sa.String(length=50), nullable=True, server_default="Movie"),
    )
    op.alter_column("movies", "content_type", server_default=None)


def downgrade() -> None:
    op.drop_column("movies", "content_type")
