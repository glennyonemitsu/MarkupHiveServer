"""create account tables

Revision ID: 45397d2b8309
Revises: 1b8ef50182c6
Create Date: 2013-04-17 13:07:27.125362

"""

# revision identifiers, used by Alembic.
revision = '45397d2b8309'
down_revision = '1b8ef50182c6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# tables to change application_id to account_id or back
tables = ['application_api_key', 'application_user']
app_tables = [  'application_route', 'application_static_file', 
                'application_static_content', 'application_template']

def upgrade():
    for t in tables:
        op.alter_column(t, 'application_id', name='account_id')

    op.rename_table('application', 'account')
    op.execute('alter sequence application_id_seq rename to account_id_seq')

    op.rename_table('application_api_key', 'account_api_key')
    op.execute('alter sequence application_api_key_id_seq rename to account_api_key_id_seq')

    op.rename_table('application_user', 'account_user')
    op.execute('alter sequence application_user_id_seq rename to account_user_id_seq')

    # adding new application table linking account and application data
    op.create_table(
        'application',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer))
    op.create_foreign_key(
        'fk_application_account_id',
        'application', 'account',
        ['account_id'], ['id'],
        onupdate='CASCADE', ondelete='CASCADE')
    op.create_index(
        'idx_application_account_id', 'application', ['account_id'])

    for atable in app_tables:
        op.alter_column(atable, 'application_id', name='account_id')
        op.add_column(atable, sa.Column('application_id', sa.Integer))
        op.create_foreign_key(
            '{table}_appinstance_fkey'.format(table=atable),
            atable, 'application',
            ['application_id'], ['id'],
            onupdate='CASCADE', ondelete='CASCADE')

    # binding from account to application
    conn = op.get_bind()
    rows = conn.execute('select id from account')
    app_table = table(
        'application', column('account_id', sa.Integer))
    app_route_table = table(
        'application_route', 
        column('account_id', sa.Integer),
        column('application_id', sa.Integer))
    app_static_file_table = table(
        'application_static_file', 
        column('account_id', sa.Integer),
        column('application_id', sa.Integer))
    app_static_content_table = table(
        'application_static_content', 
        column('account_id', sa.Integer),
        column('application_id', sa.Integer))
    app_template_table = table(
        'application_template', 
        column('account_id', sa.Integer),
        column('application_id', sa.Integer))
    app_subtables = [app_route_table, app_static_file_table, 
                     app_static_content_table, app_template_table]

    for row in rows:
        account_id = row[0]
        conn.execute(app_table.insert().values(account_id=account_id))
    rows = conn.execute('select id, account_id from application')
    # got new application ids, now to populate all the other tables
    # 'application_route', 'application_static_file', 
    # 'application_static_content', 'application_template'
    for app_id, account_id in rows:
        for subtable in app_subtables:
            stmt = subtable.\
                update().\
                values(application_id=app_id).\
                where(subtable.c.account_id==account_id)
            conn.execute(stmt)
    for atable in app_tables:
        op.drop_column(atable, 'account_id')

def downgrade():
    for table in app_tables:
        op.drop_constraint(
            '{table}_appinstance_fkey'.format(table=table),
            table)
        op.drop_column(table, 'application_id')
        op.alter_column(table, 'account_id', name='application_id')
    op.drop_table('application')

    op.rename_table('account', 'application')
    op.execute('alter sequence account_id_seq rename to application_id_seq')

    op.rename_table('account_api_key', 'application_api_key')
    op.execute('alter sequence account_api_key_id_seq rename to application_api_key_id_seq')

    op.rename_table('account_user', 'application_user')
    op.execute('alter sequence account_user_id_seq rename to application_user_id_seq')

    for table in tables:
        op.alter_column(table, 'account_id', name='application_id')
