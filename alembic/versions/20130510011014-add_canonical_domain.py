"""add canonical domain column to account

Revision ID: 1efbbd8d6721
Revises: 1e0b325c185e
Create Date: 2013-05-10 01:10:14.676068

"""

# revision identifiers, used by Alembic.
revision = '1efbbd8d6721'
down_revision = '1e0b325c185e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'account',
        sa.Column('canonical_domain', sa.String(250), nullable=True)
    )


def downgrade():
    op.drop_column('account', 'canonical_domain')
