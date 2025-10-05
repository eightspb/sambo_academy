"""Add unique index for active subscriptions per student

Revision ID: 31b85b2eb447
Revises: 0c9a9b94f082
Create Date: 2025-10-05 22:56:04.522518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31b85b2eb447'
down_revision = '0c9a9b94f082'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание уникального индекса для активных абонементов
    # Гарантирует, что у студента может быть только один активный абонемент
    op.create_index(
        'idx_one_active_subscription_per_student',
        'subscriptions',
        ['student_id'],
        unique=True,
        postgresql_where=sa.text('is_active = true')
    )


def downgrade() -> None:
    # Удаление уникального индекса
    op.drop_index(
        'idx_one_active_subscription_per_student',
        table_name='subscriptions',
        postgresql_where=sa.text('is_active = true')
    )
