"""application template cleanup

Revision ID: e52a51870d
Revises: 15f7c6560b50
Create Date: 2013-04-11 20:39:11.337162

"""

# revision identifiers, used by Alembic.
revision = 'e52a51870d'
down_revision = '15f7c6560b50'

from alembic import op
import sqlalchemy as sa



def upgrade():
    op.drop_column('application_template', 'cache_key')
    op.drop_column('application_template', 'cache_bytecode')
    op.drop_column('application_template', 'template_key')
    op.drop_column('application_template', 'template_source')


def downgrade():
    pass
