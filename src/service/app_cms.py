'''
utility functions to query the CMS for use in apps

All CMS related API endpoints should use these functions.
All app related API calls should use these as well to ensure SDK cms objects
will get the same type of data, since the SDK calls the online cms API.

cms_<query_name>
    entries (type, limit, offset)
    entry (uuid/slug)
    entry_by_uuid
    entry_by_slug
'''
from collections import namedtuple
from types import StringTypes

from flask import g
from sqlalchemy.orm.exc import NoResultFound

from server_global import db
from model.cms import ContentEntry, ContentType


def content_types():
    types = []
    for ctype in g.account.content_types:
        content_type = {'uuid': ctype.uuid,
                        'name': ctype.name,
                        'description': ctype.description}
        types.append(content_type)
    return types


def entry(slug=None, uuid=None, timezone='UTC', status='Published'):
    if (slug and uuid) or (slug is None and uuid is None):
        return {}

    elif slug:
        entry = ContentEntry.find_by_slug(slug, status)

    elif uuid:
        entry = ContentEntry.find_by_uuid(uuid, status)

    if entry is not None:
        return entry.app_data(timezone)
    else:
        return {}


def entries(content_type, page=0, limit=10, timestamp=[], timezone='UTC', tags=[], status='Published'):
    account_id = g.account.id
    page = int(page)
    limit = int(limit)

    if type(content_type) in StringTypes:
        try:
            ctype = db.session.query(ContentType).\
                filter(ContentType.account_id==account_id, 
                       ContentType.name==content_type).one()
        except NoResultFound:
            return []
    else:
        ctype = content_type

    entries = ctype.entries_query(
        page=page, 
        limit=limit, 
        timestamp=timestamp,
        timezone=timezone,
        tags=tags,
        status=status
    )
    count = ctype.entries_query_count(
        timestamp=timestamp,
        timezone=timezone,
        tags=tags,
        status=status
    )

    pages = count / limit
    if pages > 0:
        pages += 1 if count % limit > 0 else 0

    page_next = pages > page
    page_prev = page > 0

    return {'entries': entries,
            'page_next': page_next,
            'page_prev': page_prev,
            'pages': pages,
            'count': count}


class CMSUtil(object):
    pass

CMSUtil.content_types = staticmethod(content_types)
CMSUtil.entries = staticmethod(entries)
CMSUtil.entry = staticmethod(entry)
    

cms = CMSUtil()

