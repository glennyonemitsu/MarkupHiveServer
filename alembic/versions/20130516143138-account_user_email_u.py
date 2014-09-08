"""account user email unique constraint

Revision ID: 1ab21ab3dd9f
Revises: 1efbbd8d6721
Create Date: 2013-05-16 14:31:38.691371

"""

# revision identifiers, used by Alembic.
revision = '1ab21ab3dd9f'
down_revision = '1efbbd8d6721'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint(
        'uniq_account_user_account_id_email',
        'account_user',
        ['account_id', 'email'])


def downgrade():
    op.drop_constraint('uniq_account_user_account_id_email', 'account_user')
