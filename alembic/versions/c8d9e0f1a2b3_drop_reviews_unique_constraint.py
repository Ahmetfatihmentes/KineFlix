"""drop reviews unique constraint for long texts

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-06-18 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_reviews_movie_text_critic", "reviews", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_reviews_movie_text_critic",
        "reviews",
        ["movie_id", "review_text", "critic_name"],
    )
