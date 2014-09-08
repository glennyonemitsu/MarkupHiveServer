from datetime import datetime, timedelta

from flask import Flask, current_app, make_response, request
from markdown import markdown
import pyjade
from pyjade.ext.jinja import PyJadeExtension

from server_global import config, db, rds
from service import dns_cname, is_muh_domain, url_builder_manager
from service.app import response_account_not_found
from service.flask_utils import UUIDConverter


class MarkupHiveDispatcher(object):
    '''
    Dispatcher for all web servers.

    Determins if the domain suffix is for Markup Hive or additional checks are
    required for custom domains via CNAME DNS records.
    '''

    def __init__(self, muh_server):
        self.muh = muh_server

    def account_not_found(self, start_response):
        '''
        Sends a 404 and "Account not found" message
        '''
        status = '404 Not Found'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Account not found']

    def __call__(self, environ, start_response):
        hostname = environ['HTTP_HOST']
        environ['MUH_HTTP_HOST'] = hostname
        if not is_muh_domain(hostname):
            with self.muh.app_context():
                try:
                    rds_key = 'custom_domain:{domain}'.format(domain=hostname)
                    destination = rds.get(rds_key)

                    # expired or never cached. The "is None" check is used
                    # because an empty string might be cached, meaning we
                    # previously determined there is no CNAME record in DNS
                    if destination is None:
                        answer = dns_cname(hostname)
                        # got a valid CNAME
                        if answer:
                            environ['HTTP_HOST'] = answer[1]
                            environ['MUH_IS_CUSTOM_DOMAIN'] = True
                            rds.setex(rds_key, answer[2], answer[1])
                        # no CNAME exists so add an empty cache for 1 hour
                        else:
                            rds.setex(rds_key, 3600, '')
                            raise
                    # use the cache
                    elif destination == '':
                        raise
                    else:
                        environ['HTTP_HOST'] = destination
                        environ['MUH_IS_CUSTOM_DOMAIN'] = True
                    return current_app.wsgi_app(environ, start_response)
                except Exception as e:
                    return self.account_not_found(start_response)
        else:
            environ['MUH_IS_CUSTOM_DOMAIN'] = False
        return self.muh(environ, start_response)


PyJadeExtension.options['pretty'] = False
flask_app = Flask('application')
flask_app.config.from_object(config.BaseConfig)
flask_app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
flask_app.url_build_error_handlers.append(url_builder_manager)
flask_app.url_map.converters['uuid'] = UUIDConverter



db.init_app(flask_app)

wsgi_app = MarkupHiveDispatcher(flask_app)

@pyjade.register_filter('markdown')
def pyjade_filter_markdown(text, ast):
    return markdown(text)


