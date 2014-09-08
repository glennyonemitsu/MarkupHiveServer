"""cms models

Revision ID: 4bdba2a053e6
Revises: 28082259b38e
Create Date: 2013-04-19 00:26:06.759896

"""

# revision identifiers, used by Alembic.
revision = '4bdba2a053e6'
down_revision = '28082259b38e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, HSTORE
from sqlalchemy.sql.expression import text


def upgrade():
    op.create_table(
        'content_type', 
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('order', sa.Integer),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(250), nullable=False),
        sa.Column(
            'account_id', 
            sa.Integer, 
            ForeignKey('account.id', onupdate='CASCADE', ondelete='CASCADE'), 
            nullable=False)
    )
    op.create_index('idx_content_type_name', 'content_type', ['name'])
    op.create_index('idx_content_type_order', 'content_type', ['order'])
    op.create_unique_constraint(
        'uniq_content_type_account_id_name', 
        'content_type', 
        ['account_id', 'name'])

    op.create_table(
        'content_field_group', 
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('order', sa.Integer),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column(
            'content_type_uuid', 
            UUID, 
            ForeignKey('content_type.uuid', onupdate='CASCADE', ondelete='CASCADE'), 
            nullable=False)
    )
    op.create_index(
        'idx_content_field_group_order', 
        'content_field_group', 
        ['order'])
    op.create_unique_constraint(
        'uniq_content_field_group_type_id_name', 
        'content_field_group', 
        ['content_type_uuid', 'name'])

    op.create_table(
        'content_field', 
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('order', sa.Integer),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type_key', sa.String(40), nullable=False),
        sa.Column(
            'content_field_group_uuid', 
            UUID, 
            ForeignKey('content_field_group.uuid', onupdate='CASCADE', ondelete='CASCADE'), 
            nullable=False),
        sa.Column(
            'content_type_uuid', 
            UUID, 
            ForeignKey('content_type.uuid', onupdate='CASCADE', ondelete='CASCADE'), 
            nullable=False)
    )
    op.create_index('idx_content_field_order', 'content_field', ['order'])
    op.create_unique_constraint(
        'uniq_content_field_type_id_name', 
        'content_field', 
        ['content_type_uuid', 'name'])

    op.create_table(
        'content_field_type', 
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
    )

    op.create_table(
        'content_entry', 
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column(
            'account_id', sa.Integer, 
            ForeignKey('account.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=True
        ),
        sa.Column(
            'content_type_uuid', UUID, 
            ForeignKey('content_type.uuid', onupdate='CASCADE', ondelete='CASCADE')
        ),
        sa.Column('title', sa.String(200)),
        sa.Column('slug', sa.String(200)),
        sa.Column('timestamp', sa.DateTime(True), server_default=text('now()')),
    )
    op.create_index(
        'idx_content_entry_account_id', 
        'content_entry', 
        ['account_id'])
    op.create_index(
        'idx_content_entry_type_uuid', 
        'content_entry', 
        ['content_type_uuid', 'timestamp'])
    op.create_unique_constraint(
        'idx_content_entry_account_slug', 
        'content_entry', 
        ['account_id', 'slug'])

    op.create_table(
        'content_revision', 
        sa.Column('uuid', UUID, primary_key=True, server_default=text('uuid_generate_v4()')),
        sa.Column(
            'content_entry_uuid', UUID, 
            ForeignKey('content_entry.uuid', onupdate='CASCADE', ondelete='CASCADE')
        ),
        sa.Column(
            'account_user_id', sa.Integer, 
            ForeignKey('account_user.id', onupdate='CASCADE', ondelete='SET NULL'),
            nullable=True
        ),
        sa.Column('timestamp', sa.DateTime(True), server_default=text('now()')),
        sa.Column('field_data', HSTORE)
    )
    op.create_index(
        'idx_content_revision_timestamp', 
        'content_revision', 
        ['timestamp'])

    op.add_column(
        'content_entry',
        sa.Column(
            'current_revision_uuid', UUID, 
            ForeignKey('content_revision.uuid', onupdate='CASCADE', ondelete='SET NULL'),
            nullable=True
        ),
    )


def downgrade():
    op.execute('drop table content_entry cascade')
    op.drop_table('content_revision')

    op.drop_table('content_field_type')
    op.drop_table('content_field')
    op.drop_table('content_field_group')
    op.drop_table('content_type')
