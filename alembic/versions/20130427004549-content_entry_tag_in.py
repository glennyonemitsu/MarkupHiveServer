"""content entry tag indexing

Revision ID: 15c9af39a248
Revises: 5490d96894c5
Create Date: 2013-04-27 00:45:49.677457

"""

# revision identifiers, used by Alembic.
revision = '15c9af39a248'
down_revision = '5490d96894c5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('create index gin_idx_content_entry_account_id_tags '
               'on content_entry (account_id, tag)')
    #op.execute('create index gin_idx_content_entry_tags ' 'on content_entry using gin (account_ud, tag) with (fastupdate = off)')
    #op.execute('create index idx_content_entry_account on content_entry (account_id)')


def downgrade():
    op.execute('drop index gin_idx_content_entry_account_id_tags')
    #op.execute('drop index idx_content_entry_account')
