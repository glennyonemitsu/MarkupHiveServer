"""account user to application user

Revision ID: 3bc6e35fc926
Revises: 342f12ea46ed
Create Date: 2013-04-02 14:06:59.284884

"""

# revision identifiers, used by Alembic.
revision = '3bc6e35fc926'
down_revision = '342f12ea46ed'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('account_user', 'application_user')
    op.execute('alter sequence account_user_id_seq rename to application_user_id_seq')


def downgrade():
    op.rename_table('application_user', 'account_user')
    op.execute('alter sequence application_user_id_seq rename to account_user_id_seq')
