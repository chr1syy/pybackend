"""add_owner_id_to_projects_and_calculations

Revision ID: 005460fe7e6c
Revises: 3d86796db249
Create Date: 2025-12-04 07:46:00.103922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005460fe7e6c'
down_revision: Union[str, Sequence[str], None] = '3d86796db249'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add owner_id to projects table
    op.add_column('projects', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_projects_owner_id', 'projects', 'users', ['owner_id'], ['id'])

    # Add owner_id to cable_calculations table
    op.add_column('cable_calculations', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_cable_calculations_owner_id', 'cable_calculations', 'users', ['owner_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign keys and columns
    op.drop_constraint('fk_cable_calculations_owner_id', 'cable_calculations', type_='foreignkey')
    op.drop_column('cable_calculations', 'owner_id')

    op.drop_constraint('fk_projects_owner_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'owner_id')
