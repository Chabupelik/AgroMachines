"""add_admin_role_to_enum

Revision ID: 07e6d398a8ea
Revises: 7f7fd54c745f
Create Date: 2026-06-03 14:01:07.882535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07e6d398a8ea'
down_revision: Union[str, None] = '7f7fd54c745f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE role_enum ADD VALUE 'ADMIN'")


def downgrade() -> None:
    pass