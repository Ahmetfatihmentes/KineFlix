"""add reviews table

Revision ID: 9e216421e288
Revises: a1b2c3d4e5f6
Create Date: 2026-06-17 12:15:34.423126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9e216421e288"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.String(length=50), nullable=True),
        sa.Column("critic_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "movie_id",
            "review_text",
            "critic_name",
            name="uq_reviews_movie_text_critic",
        ),
    )
    op.create_index(op.f("ix_reviews_movie_id"), "reviews", ["movie_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_movie_id"), table_name="reviews")
    op.drop_table("reviews")
