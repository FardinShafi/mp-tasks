"""Add created_by and updated_by to Dashboard

Revision ID: b0b55abe78b6
Revises: 2085bdcb27c9
Create Date: 2024-06-10 16:20:35.764832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0b55abe78b6'
down_revision: Union[str, None] = '2085bdcb27c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'dashboards',
        sa.Column('id', sa.String(), primary_key=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('updated_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False, onupdate=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('dashboards')
