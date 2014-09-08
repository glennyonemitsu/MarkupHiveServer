"""content entry status

Revision ID: 1e0b325c185e
Revises: 15c9af39a248
Create Date: 2013-05-01 12:14:42.027136

"""

# revision identifiers, used by Alembic.
revision = '1e0b325c185e'
down_revision = '15c9af39a248'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import table, column


def upgrade():
    op.create_table(
        'content_type_status',
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column(
            'content_type_uuid', 
            UUID, 
            sa.ForeignKey(
                'content_type.uuid', 
                ondelete='CASCADE',
                onupdate='CASCADE')),
        sa.Column('order', sa.Integer),
        sa.Column('name', sa.String(30)),
    )
    op.create_index(
        'idx_content_type_status_type_uuid',
        'content_type_status',
        ['content_type_uuid', 'order']
    )
    op.create_unique_constraint(
        'uniq_content_type_uuid_name', 
        'content_type_status',
        ['content_type_uuid', 'name']
    )

    op.add_column(
        'content_entry',
        sa.Column(
            'content_type_status_uuid', 
            UUID, 
            sa.ForeignKey(
                'content_type_status.uuid',
                ondelete='SET NULL',
                onupdate='CASCADE'))
    )
    op.create_foreign_key(
        'fkey_content_entry_type_status_uuid',
        'content_entry', 'content_type_status',
        ['content_type_status_uuid'], ['uuid'],
        onupdate='CASCADE', ondelete='SET NULL'
    )

    # prepopulate type status tables with 'draft' and 'published' 
    status_table = table(
        'content_type_status', 
        column('uuid', UUID),
        column('content_type_uuid', UUID),
        column('order', sa.Integer),
        column('name', sa.String(30))
    )
    entry_table = table(
        'content_entry', 
        column('uuid', UUID),
        column('content_type_status_uuid', UUID),
    )

    conn = op.get_bind()
    types = conn.execute('select uuid from content_type')
    for t in types:
        type_uuid = t[0]
        op.bulk_insert(
            status_table,
            [{'content_type_uuid': type_uuid, 'order': 0, 'name': 'Draft'},
             {'content_type_uuid': type_uuid, 'order': 1, 'name': 'Published'}]
        )

    status_map = {}
    stats = conn.execute('select uuid, content_type_uuid, name from content_type_status')
    for status in stats:
        uuid, ctuuid, name = status
        if name == 'Published':
            status_map[ctuuid] = uuid

    entries = conn.execute('select uuid, content_type_uuid from content_entry')
    for entry in entries:
        cuuid = entry[0]
        suuid = status_map[entry[1]]
        update = entry_table.\
            update().\
            values(content_type_status_uuid=suuid).\
            where(entry_table.c.uuid==cuuid)
        conn.execute(update)


def downgrade():
    op.drop_column('content_entry', 'content_type_status_uuid')
    op.drop_table('content_type_status')


