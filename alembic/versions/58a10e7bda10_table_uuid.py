"""table uuid

Revision ID: 58a10e7bda10
Revises: 130f250d07cc
Create Date: 2024-06-10 18:21:21.506603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '58a10e7bda10'
down_revision: Union[str, None] = '130f250d07cc'
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

    op.create_table(
        'dashboard_components',
        sa.Column('id', sa.String(), primary_key=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('property', sa.JSON(), nullable=False),
        sa.Column('data_property', sa.JSON(), nullable=False),
        sa.Column('filter_property', sa.JSON(), nullable=False),
        sa.Column('dashboard_id', sa.String(), sa.ForeignKey('dashboards.id', name='fk_dashboard_components_dashboard_id', ondelete='CASCADE'), nullable=False)
    )


def downgrade():
    op.drop_table('dashboard_components')
    op.drop_table('dashboards')