'''
API endpoints for use only by the SDK

GET /cms/content_types/

GET /cms/content_type/<ctype_uuid>/

GET /cms/entries/<ctype_uuid>/
    ? page, limit

GET /cms/entry/<entry_uuid>/
'''
from sqlalchemy.exc import SQLAlchemyError

from flask import current_app, request, g

from server_global import db
from service import app_cms as cms

from application.blueprint import api as bp
from application.api.exception import APIError
from application.api.view import api_reply, check_signature


@bp.route('/cms/content-types/', versions=[1], methods=['GET'])
@api_reply
@check_signature
def content_types():
    '''
    cms content types
    does not include field groups or fields
    '''
    return cms.content_types()
    types = []
    for ctype in g.account.content_types:
        content_type = {'uuid': ctype.uuid,
                        'name': ctype.name,
                        'description': ctype.description}
        types.append(content_type)
    return types


@bp.route('/cms/entries/', versions=[1], methods=['GET'])
@api_reply
@check_signature
def entries():
    '''
    cms content entries
    '''
    type_name = request.args.get('type_name')
    page = request.args.get('page', 0)
    limit = request.args.get('limit', 10)
    timestamp = request.args.get('timestamp', [])
    timezone = request.args.get('timezone', 'UTC')
    tags = request.args.get('tags', [])
    status = request.args.get('status', ['Published'])

    return cms.entries(type_name, 
                       page, 
                       limit, 
                       timestamp=timestamp, 
                       timezone=timezone,
                       tags=tags, 
                       status=status)


@bp.route('/cms/entry/', versions=[1], methods=['GET'])
@api_reply
@check_signature
def entry():
    '''
    cms content entries
    '''
    status = request.args.get('status', ['Published'])
    uuid = request.args.get('uuid')
    slug = request.args.get('slug')
    timezone = request.args.get('timezone', 'UTC')

    return cms.entry(uuid=uuid, slug=slug, timezone=timezone, status=status)

