"""template table moved to preprocessed format

Revision ID: 2653209f57fe
Revises: 3bc6e35fc926
Create Date: 2013-04-03 22:54:15.357420

"""

# revision identifiers, used by Alembic.
revision = '2653209f57fe'
down_revision = '3bc6e35fc926'

from alembic import op
import sqlalchemy as sa

from pyjade.utils import process
from pyjade.ext.jinja import Compiler

def upgrade():
    op.add_column('application_template', sa.Column('jinja2', sa.Text))
    op.add_column('application_template', sa.Column('key', sa.String(255)))


    meta = sa.MetaData()
    table = sa.schema.Table(
        'application_template', meta,
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('key', sa.String(255)),
        sa.Column('jinja2', sa.Text)
    )

    # converting original jade template_source into jinja2 preprocessed source
    conn = op.get_bind()
    rows = conn.execute('select id, template_key, template_source from application_template')
    for row in rows:
        rid = row[0]
        name = row[1]
        source = row[2]
        results = process(source,filename=name,compiler=Compiler)
        where = 'id=%d' % rid
        update_expression = sa.sql.expression.update(
            table, whereclause=where,
            values={
                'jinja2': results,
                'key': name
            }
        )
        conn.execute(update_expression)


def downgrade():
    op.drop_column('application_template', 'jinja2')
    op.drop_column('application_template', 'key')
