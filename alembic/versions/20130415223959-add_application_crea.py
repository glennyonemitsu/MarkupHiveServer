"""add application create timestamp column

Revision ID: 1b8ef50182c6
Revises: 15c467143dc2
Create Date: 2013-04-15 22:39:59.960401

"""

# revision identifiers, used by Alembic.
revision = '1b8ef50182c6'
down_revision = '15c467143dc2'

from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade():
    
    dt = datetime(2013, 4, 1)
    op.add_column('application', sa.Column('join_timestamp', sa.DateTime))

    app_table = table('application', column('join_timestamp', sa.DateTime))

    conn = op.get_bind()
    updates = sa.sql.expression.update(
        app_table,
        values={'join_timestamp': dt})
    conn.execute(updates)


def downgrade():
    op.drop_column('application', 'join_timestamp')
