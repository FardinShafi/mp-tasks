"""Create dashboard and dashboard_components deleting order

Revision ID: c0188b873f04
Revises: 836c92171a3b
Create Date: 2024-06-10 17:06:19.337953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0188b873f04'
down_revision: Union[str, None] = '836c92171a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the dashboards table with CASCADE option
    op.execute('DROP TABLE IF EXISTS dashboards CASCADE')
    
    # Create the dashboards table
    op.create_table(
        'dashboards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create the dashboard_components table
    op.create_table(
        'dashboard_components',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('dashboard_id', sa.String(), nullable=True),
        sa.Column('component_type', sa.String(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('position', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop the dashboard_components table
    op.drop_table('dashboard_components')
    
    # Drop the dashboards table
    op.drop_table('dashboards')

