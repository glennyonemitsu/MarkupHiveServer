"""application custom domains

Revision ID: 15f7c6560b50
Revises: 2653209f57fe
Create Date: 2013-04-10 16:29:31.805838

"""

# revision identifiers, used by Alembic.
revision = '15f7c6560b50'
down_revision = '2653209f57fe'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'custom_domain', 
        sa.Column('source', sa.String(255), primary_key=True, unique=True),
        sa.Column('destination', sa.String(255)),
        sa.Column('expiration', sa.DateTime))


def downgrade():
    op.drop_table('custom_domain')
