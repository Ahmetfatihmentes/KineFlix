"""add themes column to movies

Revision ID: a1b2c3d4e5f6
Revises: fb177eecdb7d
Create Date: 2026-06-17 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "fb177eecdb7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("themes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("movies", "themes")
