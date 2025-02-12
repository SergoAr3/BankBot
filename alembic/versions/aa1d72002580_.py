"""

Revision ID: aa1d72002580
Revises: cd91062f48e8
Create Date: 2025-01-29 22:10:03.742993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa1d72002580'
down_revision: Union[str, None] = 'cd91062f48e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column('deposits', 'term')

    op.execute(
        "ALTER TABLE credits ALTER COLUMN term TYPE TIMESTAMP WITHOUT TIME ZONE USING to_timestamp(term) AT TIME ZONE 'UTC'")



def downgrade():
    op.add_column('deposits', sa.Column('term', sa.INTEGER(), autoincrement=False, nullable=False))

    op.execute("ALTER TABLE credits ALTER COLUMN term TYPE INTEGER USING EXTRACT(EPOCH FROM term)::INTEGER")

