"""plan code name field

Revision ID: 15c467143dc2
Revises: 1edb643716c3
Create Date: 2013-04-14 19:42:26.867477

"""

# revision identifiers, used by Alembic.
revision = '15c467143dc2'
down_revision = '1edb643716c3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade():
    op.add_column(
        'application', 
        sa.Column('plan_code_name', sa.String(200)))
    app_table = table(
        'application', 
        column('plan_code_name', sa.String(200)))

    conn = op.get_bind()
    updates = sa.sql.expression.update(
        app_table,
        values={'plan_code_name': 'beta test'})
    conn.execute(updates)


def downgrade():
    op.drop_column('application', 'plan_code_name')
