"""Added user table

Revision ID: 2bb9a2475f84
Revises: 
Create Date: 2026-06-09 20:44:40.203988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bb9a2475f84'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=32), nullable=False),
        sa.Column('password_hash', sa.String(length=60), nullable=False),
        sa.Column('display_number', sa.BigInteger(), sa.Identity(always=False, start=10000, increment=1), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('display_number')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
