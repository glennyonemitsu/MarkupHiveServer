"""account and application indexes

Revision ID: 2bd23c70af40
Revises: 45397d2b8309
Create Date: 2013-04-17 23:27:35.325301

"""

# revision identifiers, used by Alembic.
revision = '2bd23c70af40'
down_revision = '45397d2b8309'

from alembic import op
import sqlalchemy as sa


indexes = [
    ('idx_account_api_key_account_id', 'account_api_key', 'account_id'),
    ('idx_account_user_account_id', 'account_user', 'account_id'),
    ('idx_application_route_appinstance_id', 'application_route', 'application_id'),
    ('idx_application_static_content_appinstance_id', 'application_static_content', 'application_id'),
    ('idx_application_static_file_appinstance_id', 'application_static_file', 'application_id'),
    ('idx_application_template_appinstance_id', 'application_template', 'application_id'),
]

def upgrade():
    for index in indexes:
        op.create_index(index[0], index[1], [index[2]])
    op.execute('alter table application_route add constraint uniq_app_route_appid_rule unique(application_id, rule)')
    op.execute('alter table application_static_content add constraint uniq_app_static_content_appid_resource_key unique(application_id, resource_key)')
    op.execute('alter table application_static_file add constraint uniq_app_static_file_appid_resource_key unique(application_id, resource_key)')
    op.execute('alter table application_template add constraint uniq_app_template_appid_key unique(application_id, key)')


def downgrade():
    for index in indexes:
        op.drop_index(index[0], index[1])
    op.execute('alter table application_route drop constraint if exists uniq_app_route_appid_rule')
    op.execute('alter table application_static_content drop constraint if exists uniq_app_static_content_appid_resource_key')
    op.execute('alter table application_static_file drop constraint if exists uniq_app_static_file_appid_resource_key')
    op.execute('alter table application_template drop constraint if exists uniq_app_template_appid_key')
