"""Add additional groups to students

Revision ID: fb7d6dc9bb22
Revises: 31b85b2eb447
Create Date: 2025-10-05 23:59:03.404501

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fb7d6dc9bb22'
down_revision = '31b85b2eb447'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add additional_group_ids column to students table
    op.add_column('students', 
        sa.Column('additional_group_ids', 
                  postgresql.ARRAY(postgresql.UUID(as_uuid=True)), 
                  nullable=True,
                  server_default='{}'))


def downgrade() -> None:
    # Remove additional_group_ids column
    op.drop_column('students', 'additional_group_ids')
