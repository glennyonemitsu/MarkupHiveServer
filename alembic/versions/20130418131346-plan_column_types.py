"""plan column types

Revision ID: 28082259b38e
Revises: 2bd23c70af40
Create Date: 2013-04-18 13:13:46.621908

"""

# revision identifiers, used by Alembic.
revision = '28082259b38e'
down_revision = '2bd23c70af40'

from alembic import op
import sqlalchemy as sa


columns = ['transfer', 'size_total', 'size_static']

def upgrade():
    for col in columns:
        op.alter_column('plan', col, type_=sa.BigInteger)
        op.alter_column('account', col, type_=sa.BigInteger)


def downgrade():
    for col in columns:
        op.alter_column('plan', col, type_=sa.Integer)
        op.alter_column('account', col, type_=sa.Integer)
