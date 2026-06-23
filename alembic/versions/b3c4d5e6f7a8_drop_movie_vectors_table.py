"""drop movie_vectors table

Revision ID: b3c4d5e6f7a8
Revises: d7125bcb582d
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "d7125bcb582d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("movie_vectors")


def downgrade() -> None:
    op.create_table(
        "movie_vectors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "movie_id",
            sa.Integer(),
            sa.ForeignKey("movies.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("vector_blob", sa.LargeBinary(), nullable=False),
    )
