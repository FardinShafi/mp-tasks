"""Create dashboard and dashboard_components table

Revision ID: 017a534fc005
Revises: b0b55abe78b6
Create Date: 2024-06-10 16:43:38.206559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '017a534fc005'
down_revision: Union[str, None] = 'b0b55abe78b6'
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
        sa.Column('dashboard_id', sa.String(), sa.ForeignKey('dashboards.id'), nullable=False)
    )

def downgrade():
    op.drop_table('dashboard_components')
    op.drop_table('dashboards')