"""content entry tag array column

Revision ID: 5490d96894c5
Revises: 4bdba2a053e6
Create Date: 2013-04-26 16:44:40.661659

"""

# revision identifiers, used by Alembic.
revision = '5490d96894c5'
down_revision = '4bdba2a053e6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


def upgrade():
    op.add_column(
        'content_entry',
        sa.Column('tag', ARRAY(sa.String(20)))
    )
    op.create_unique_constraint(
        'uniq_content_entry_uuid_tag',
        'content_entry',
        ['uuid', 'tag'])


def downgrade():
    op.drop_constraint('uniq_content_entry_uuid_tag', 'content_entry')
    op.drop_column('content_entry', 'tag')
