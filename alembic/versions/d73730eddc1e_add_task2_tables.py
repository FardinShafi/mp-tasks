"""Add task2 tables

Revision ID: d73730eddc1e
Revises: 58a10e7bda10
Create Date: 2024-06-12 11:26:01.318402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd73730eddc1e'
down_revision: Union[str, None] = '58a10e7bda10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'department' not in tables:
        op.create_table(
            'department',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(), nullable=False)
        )

    if 'guardian' not in tables:
        op.create_table(
            'guardian',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('contact_number', sa.String(), nullable=True)
        )

    # Create employee table
    op.create_table(
        'employee',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('department', sa.String(), nullable=False),
        sa.Column('is_manager', sa.Boolean(), nullable=False, default=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('department.id', name='fk_employee_department_id'), nullable=True)
    )

    # Create student table
    op.create_table(
        'student',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('enrollment_date', sa.Date(), nullable=True),
        sa.Column('guardian_id', sa.Integer(), sa.ForeignKey('guardian.id', name='fk_student_guardian_id'), nullable=True)
    )

    # Create tables table
    op.create_table(
        'tables',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('table_name', sa.String(), unique=True, nullable=False)
    )

    # Create vendor table
    op.create_table(
        'vendor',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_number', sa.String(), nullable=True)
    )


def downgrade():
    op.drop_table('vendor')
    op.drop_table('tables')
    op.drop_table('guardian')
    op.drop_table('student')
    op.drop_table('employee')
    op.drop_table('department')
