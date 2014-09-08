import base64
import copy
from datetime import datetime, timedelta
import json
import os.path
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError

from flask import current_app, request, g, make_response
import markdown
import scss
import yaml

from application.blueprint import api as bp
from model import \
    Account, AccountUser, AccountAPIKey, \
    ApplicationStaticContent, ApplicationStaticFile, \
    ApplicationRoute, ApplicationTemplate, \
    Application, \
    Plan
import service
from service import mailer
from server_global import config, db

from application.api.exception import APIError


bp.url_value_preprocessor(service.url_values_manager)


# CORS support. Headers only sent for non 404/500 responses
@bp.after_request
def cors(res):
    referer = service.extract_domain(request.environ.get('HTTP_REFERER'))
    sources = config.CORS_SOURCE
    if sources == ['*']:
        res.headers.setdefault('Access-Control-Allow-Origin', '*')
    elif referer in sources:
        res.headers.setdefault('Access-Control-Allow-Origin', host)
    return res


def api_reply(fn):
    '''
    decorator to be used on all api functions to take a dict return value
    and turn it into a JSON string.

    If any API call raised an exception, those will be dealt with the 
    registered error handlers below.

    Any callable wrapped by this must return a dict with the relavant data for
    the client. The dict key 'success' will be added with this and the 
    returned data will be under the 'result' key.
    '''
    def jsonified(*args, **kwargs):
        reply = fn(*args, **kwargs)
        response = {'success': True, 'result': reply}
        return json.dumps(response)
    jsonified.__name__ = fn.__name__
    return jsonified


def check_signature(fn):
    '''
    decorator to force the API method to verify the signature before allowing
    it to execute.
    '''
    def checked(*args, **kwargs):
        # preventing replay attacks
        date = datetime.strptime(request.headers.get('Date'), '%a, %d %b %y %H:%M:%S GMT')
        now = datetime.utcnow()
        delta = timedelta(0, 0, 0, 0, 10)
        if now - date > delta:
            raise APIError('Date header is too old. Latest allowed is 10 minutes.')

        # checking the API key exists
        authn = request.headers.get('X-Authentication', '')
        authn_access_key, authn_signature = authn.split(':')
        key_query = db.session.query(AccountAPIKey).\
            filter(AccountAPIKey.access_key==authn_access_key)
        try:
            key = key_query.one()
        except NoResultFound:
            raise APIError('Access key not found.')
        api_access_key = key.access_key
        api_secret = key.secret64()
        request_signature = service.api_signature(api_secret, request)

        # bad signature. Note the same message is still sent
        if request_signature != authn_signature:
            raise APIError('Incorrect signature.')

        g.account = key.account
        return fn(*args, **kwargs)
    checked.__name__ = fn.__name__
    return checked


@bp.errorhandler(404)
def error_handler_404(error):
    response_data = {'success': False, 'error': ['404 not found']}
    response_json = json.dumps(response_data)
    response = make_response(response_json, 404)
    return response


@bp.errorhandler(SQLAlchemyError)
def error_handler_db(error):
    response_data = {'success': False, 'error': ['Database error.']}
    response_json = json.dumps(response_data)
    response = make_response(response_json, 403)
    return response


@bp.errorhandler(APIError)
def error_handler_generic(error):
    response_data = {'success': False, 'error': error.errors}
    response_json = json.dumps(response_data)
    response = make_response(response_json, 403)
    return response
    

