"""add_is_available_to_machine

Revision ID: 91069b7cde27
Revises: 46c06a03243a
Create Date: 2026-06-03 12:25:51.128826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91069b7cde27'
down_revision: Union[str, None] = '46c06a03243a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Шаг 1. Сначала добавляем колонку как nullable=True (разрешаем пустые значения)
    op.add_column('machines', sa.Column('is_available', sa.Boolean(), nullable=True))
    
    # Шаг 2. Проставляем дефолтное значение TRUE для всех уже существующих строк в БД
    op.execute("UPDATE machines SET is_available = TRUE")
    
    # Шаг 3. Теперь, когда все старые строки заполнены, мы можем безопасно сделать колонку NOT NULL
    op.alter_column('machines', 'is_available', nullable=False)


def downgrade() -> None:
    # При откате миграции просто удаляем колонку
    op.drop_column('machines', 'is_available')
