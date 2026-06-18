"""add turkish columns to movies

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-06-18 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d9e0f1a2b3c4"
down_revision: Union[str, Sequence[str], None] = "c8d9e0f1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("overview_tr", sa.Text(), nullable=True))
    op.add_column("movies", sa.Column("tagline_tr", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("movies", "tagline_tr")
    op.drop_column("movies", "overview_tr")
