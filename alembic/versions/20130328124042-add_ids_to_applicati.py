"""add ids to application tables

Revision ID: 342f12ea46ed
Revises: None
Create Date: 2013-03-28 12:40:42.861173

"""

# revision identifiers, used by Alembic.
revision = '342f12ea46ed'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    sqls = (
        'alter table application_static_file '
        'drop constraint application_static_file_pkey',

        'alter table application_template '
        'drop constraint application_template_pkey',

        'alter table application_api_key '
        'add column id bigserial primary key',

        'alter table application_static_file '
        'add column id bigserial primary key',

        'alter table application_template '
        'add column id bigserial primary key',
    )

    for sql in sqls:
        op.execute(sql)


def downgrade():
    pass
