from flask import abort, request, session, redirect, url_for, g

from application.manager.view import \
    account, api_keys, base, data_transfer, user, canonical_domain
from application.blueprint import manager as bp
from application.blueprint import cms as bp_cms
from model import Account
from server_global import config
import service


bp.url_value_preprocessor(service.url_values_manager)
bp_cms.url_value_preprocessor(service.url_values_manager)


@bp.before_request
@bp_cms.before_request
def before_request():

    uri_parts = request.url.split('/')
    domain = uri_parts[2]
    
    parts_count = len(config.DOMAIN_SUFFIX_MANAGER.split('.')) + 1

    if len(domain.split('.')) != parts_count:
        abort(403)

    account_name = domain.split('.')[0]
    account = Account.get_by_name(account_name)
    if account is None:
        abort(403)

    account_user = None
    unchecked_endpoints = ('manager.login', 
                           'manager.logout', 
                           'manager.forgot_password',
                           'manager.password_reset')
    if request.endpoint not in unchecked_endpoints and \
       uri_parts[3] != 'static':
        # is the session's user id in the account
        for user in account.users:
            if user.id == session.get('user id'):
                account_user = user

        # verify login with session data
        # if logged in, is it for this subdomain? if not, log them out and 
        # redirect to logout view, which will redirect them to login
        if not session.get('logged in') or \
           not session.get('account id') or \
           not session.get('user id') or \
           account_user is None or \
           session.get('account id') != account.id:
            return redirect(url_for('manager.login'))

    g.account = account
    g.user = account_user


