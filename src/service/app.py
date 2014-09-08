'''
Helper functions related to serving an application
'''
from datetime import datetime
from hashlib import sha1
from types import IntType, StringType

from flask import g, make_response
from redis.exceptions import RedisError

from server_global import rds

    
def record_transfer(size, account_id=None):
    '''
    Record into redis account transfer.

    is size param is not an integer, assume it's the response body and get
    size info with len()
    '''
    if not isinstance(size, int):
        size = len(size)
    if account_id is None:
        account_id = g.account.id

    dt = datetime.utcnow()
    year = dt.strftime('%Y')
    month = dt.strftime('%m')
    day = dt.strftime('%d')

    # daily aggregate
    ymd_key = 'xferd:{app_id}'.format(app_id=account_id, year=year, month=month, day=day)
    ymd_field = '{year}{month}{day}'.format(year=year, month=month, day=day)
    # month aggregate
    ym_key = 'xferm:{app_id}'.format(app_id=account_id, year=year, month=month)
    ym_field = '{year}{month}'.format(app_id=account_id, year=year, month=month)

    try:
        rds.hincrby(ymd_key, ymd_field, size)
        rds.hincrby(ym_key, ym_field, size)
    except RedisError as e:
        pass #meh


def year_month_day():
    '''
    get hash field for year, month, and day
    '''
    dt = datetime.utcnow()
    ymd = dt.strftime('%Y%m%d')
    return ymd


def year_month():
    '''
    get hash field for year and month
    '''
    dt = datetime.utcnow()
    ym = dt.strftime('%Y%m')
    return ym


def response_account_not_found():
    res = make_response('Account not found', 404)
    res.headers['Content-type'] = 'text/plain'
    return res


def response_account_transfer_exceeded():
    res = make_response("This account's has exceeded its monthly transfer limit.", 403)
    res.headers['Content-type'] = 'text/plain'
    return res


def response_account_missing():
    res = make_response("No application has yet been uploaded.", 404)
    res.headers['Content-type'] = 'text/html'
    return res


class GetUtil(object):
    '''
    Helper object to query the GET variables in the app
    '''

    def __init__(self, request):
        self.args = request.args

    def __call__(self, name):
        return self.args.get(name, '')
    
    def list(self, name):
        return self.args.getlist(name)


class PathUtil(object):
    '''
    Helper object to query the request path
    '''

    def __init__(self, environ):
        '''
        environ param is the wsgi environ dict
        '''
        path = environ.get('PATH_INFO')
        self.path = path
        self.paths = path.strip('/').split('/')
        self.placeholders = {} # url route placeholders

    def __call__(self, index=None):
        if index is None:
            return self.path
        elif type(index) is IntType and len(self.paths) > index:
            return self.paths[index]
        elif type(index) is StringType:
            return self.placeholders.get(index, '')
        return ''

    def add_placeholders(self, placeholders):
        self.placeholders = {
            k: v for k, v in placeholders.items() if not k.startswith('_')
        }


class StaticUtil(object):
    '''
    Helper object to get static paths with cache busting GET variables
    '''

    def __call__(self, path):
        s = sha1()
        s.update(str(g.account.application.id))
        cache = s.hexdigest()
        if not path.startswith('/'):
            path = '/' + path
        full_path = '/static{path}.c-{cache}'.format(path=path, cache=cache)
        return full_path
