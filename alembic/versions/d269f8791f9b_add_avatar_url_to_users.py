"""add_avatar_url_to_users

Revision ID: d269f8791f9b
Revises: 1acb5d7bb323
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d269f8791f9b"
down_revision: Union[str, Sequence[str], None] = "1acb5d7bb323"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(512), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
