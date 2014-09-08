"""add application plans

Revision ID: 1edb643716c3
Revises: e52a51870d
Create Date: 2013-04-14 14:40:45.693170

"""

# revision identifiers, used by Alembic.
revision = '1edb643716c3'
down_revision = 'e52a51870d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


def upgrade():
    op.create_table(
        'plan',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code_name', sa.String(200), unique=True),
        sa.Column('name', sa.String(200)),
        sa.Column('price', sa.Numeric(5, 2)),
        sa.Column('available', sa.Boolean),
        sa.Column('custom_domain', sa.Boolean),
        sa.Column('cms', sa.Boolean),
        sa.Column('size_total', sa.Integer, nullable=True),
        sa.Column('size_static', sa.Integer, nullable=True),
        sa.Column('transfer', sa.Integer, nullable=True),
        sa.Column('count_template', sa.Integer, nullable=True),
        sa.Column('count_static', sa.Integer, nullable=True),
    )
    plan_table = table(
        'plan',
        column('code_name', sa.String(200)),
        column('name', sa.String(200)),
        column('price', sa.Numeric(5, 2)),
        column('available', sa.Boolean),
        column('custom_domain', sa.Boolean),
        column('cms', sa.Boolean),
        column('size_total', sa.Integer),
        column('size_static', sa.Integer),
        column('transfer', sa.Integer),
        column('count_template', sa.Integer),
        column('count_static', sa.Integer)
    )
    beta_plan = {   'code_name': 'beta test',
                    'name': 'Beta Test',
                    'price': '0.00',
                    'available': True,
                    'custom_domain': True,
                    'cms': True,
                    'size_total': 0,
                    'size_static': 0,
                    'transfer': 0,
                    'count_template': 0,
                    'count_static': 0}
    op.create_index('idx_plan_id_available', 'plan', ['id', 'available'])
    op.bulk_insert(plan_table, [beta_plan])

    op.add_column('application', sa.Column('plan_name', sa.String(200)))
    op.add_column('application', sa.Column('price', sa.Numeric(5, 2)))
    op.add_column('application', sa.Column('custom_domain', sa.Boolean))
    op.add_column('application', sa.Column('cms', sa.Boolean))
    op.add_column('application', sa.Column('size_total', sa.Integer))
    op.add_column('application', sa.Column('size_static', sa.Integer))
    op.add_column('application', sa.Column('transfer', sa.Integer))
    op.add_column('application', sa.Column('count_template', sa.Integer))
    op.add_column('application', sa.Column('count_static', sa.Integer))
    op.create_index(
        'idx_application_name_custom_domain', 
        'application', 
        ['name', 'custom_domain'])
    app_table = table(
        'application', 
        column('plan_name', sa.String(200)),
        column('custom_domain', sa.Boolean),
        column('price', sa.Numeric(5, 2)),
        column('cms', sa.Boolean),
        column('size_total', sa.Integer),
        column('size_static', sa.Integer),
        column('transfer', sa.Integer),
        column('count_template', sa.Integer),
        column('count_static', sa.Integer),
    )
    conn = op.get_bind()
    updates = sa.sql.expression.update(
        app_table,
        values={'plan_name': 'Beta Test',
                'custom_domain': True,
                'price': '0.00',
                'cms': True,
                'size_total': 0,
                'size_static': 0,
                'transfer': 0,
                'count_template': 0,
                'count_static': 0}
    )
    conn.execute(updates)


def downgrade():
    op.drop_table('plan')

    op.drop_index('idx_application_name_custom_domain')
    op.drop_column('application', 'plan_name')
    op.drop_column('application', 'price')
    op.drop_column('application', 'custom_domain')
    op.drop_column('application', 'cms')
    op.drop_column('application', 'size_total')
    op.drop_column('application', 'size_static')
    op.drop_column('application', 'transfer')
    op.drop_column('application', 'count_template')
    op.drop_column('application', 'count_static')

