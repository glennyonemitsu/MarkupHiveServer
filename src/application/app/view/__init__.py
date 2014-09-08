from hashlib import sha1
import mimetypes
import StringIO
import sys

from flask import abort, current_app, request, send_file, g, make_response, redirect
from jinja2 import DictLoader
from jinja2.sandbox import SandboxedEnvironment
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound

from server_global import config, db, rds
from application.blueprint import app as bp

from model import Account, ApplicationStaticFile
import service
from service.app import year_month, PathUtil, GetUtil, StaticUtil
from service import app
from service.app_cms import cms

# we need to load PyJade for both manager and app services. We keep two 
# identical copies to serve, because they use global options. The manager uses
# default pyJade extension behavior. But since apps are precompiled into 
# jinja2, we need to load pyjade for utility functions such as __pyjade_iter
# and NOT have it reparse the app templates as jade.
from application.app.pyjade.ext.jinja import PyJadeExtension
PyJadeExtension.file_extensions = '.qweoiuwiruhsdlkjahsdflewiu'


bp.url_value_preprocessor(service.url_values_manager)


@bp.before_request
def before_request():

    # check that the wsgi's environ set to an app subdomain
    if not service.is_app_domain():
        abort(404)

    # check for app in our system
    host = request.url.split('/')[2]
    domain = host.split(':')[0]
    account_name = domain.split('.')[0]
    account = Account.get_by_name(account_name)
    if account is None:
        return app.response_account_not_found()

    # if this app served as a custom domain, check that the app is allowed
    if request.environ['MUH_IS_CUSTOM_DOMAIN'] and \
       not account.custom_domain:
        return app.response_account_not_found()
    
    # check if the account has a canonical domain setup
    if account.custom_domain and \
       account.canonical_domain and \
       account.canonical_domain != request.environ['MUH_HTTP_HOST']:
        new_url = request.url.replace(
            request.environ['HTTP_HOST'],
            account.canonical_domain,
            1
        )
        return redirect(new_url, code=301)


    # check the app is not over the current month's transfer limit
    if account.transfer: # 0 is unlimited
        rds_key = 'xferm:{account_id}'.format(account_id=account.id)
        rds_field = year_month()
        xfer = rds.hget(rds_key, rds_field)
        if xfer is not None and int(xfer) > account.transfer:
            return app.response_account_transfer_exceeded()

    # new registrations might not have any app uploaded
    if account.application is None:
        return app.response_account_missing()

    # OK, you can go now
    g.account = account
    s = sha1()
    s.update(str(g.account.application.id))
    g.application_hash = s.hexdigest()


@bp.route('/static/<path:filename>')
def static(filename):
    # etag caching?
    etag = request.headers.get('If-None-Match', '')[1:-1] # remove quotes
    if etag == g.application_hash:
        res = make_response('', 304)
        return res

    suffix = '.c-{uuid}'.format(uuid=g.application_hash)
    if filename.endswith(suffix):
        filename = filename[:-len(suffix)]
    query = db.session.query(ApplicationStaticFile.data).\
        filter_by(
            application_id=g.account.application.id,
            resource_key=filename)
    try:
        file_data = query.one()
        app.record_transfer(file_data.data)
        fileIO = StringIO.StringIO()
        fileIO.write(file_data.data)
        fileIO.seek(0)
        if filename.startswith('css/'):
            mtype = 'text/css'
        elif filename.startswith('js/'):
            mtype = 'application/javascript'
        else:
            mtype = mimetypes.guess_type(filename)[0]

        #if request.args.get('c'): # using StaticUtil for cache busting
        if filename.endswith(suffix):
            timeout = 31536000 # one year
        else:
            timeout = 3600 # one hour
        rv = send_file(fileIO, mimetype=mtype, cache_timeout=timeout)
        rv.set_etag(g.application_hash)
        return rv
    except:
        abort(404)


@bp.route('/favicon.ico')
def favicon():
    return static('favicon.ico')


@bp.route('/')
@bp.route('/<path:path>')
def server(path='/'):
    try:
        account = g.account
        application = g.account.application
        # prepare the jinja environment. This is used for regular routes 
        # and special handlers such as 404
        template_lookup = {t.key: t.jinja2 for t in application.templates}
        loader = DictLoader(template_lookup)
        jinja_env = SandboxedEnvironment(
            extensions=['application.app.pyjade.ext.jinja.PyJadeExtension'],
            loader=loader)
        
        # default helper utils
        path = PathUtil(request.environ)
        get = GetUtil(request)
        static = StaticUtil()

        # load template data. 404 can also use these
        template_data = {}
        template_data['path'] = path
        template_data['get'] = get
        template_data['cms'] = cms
        template_data['static'] = static
        template_data['deployment'] = config.TEMPLATE_GLOBAL_DEPLOYMENT
        template_data['markdown'] = service.markdown

        template_content = {}
        for content in application.static_contents:
            template_content.update(content.data)
        template_data['content'] = template_content

        # find the route with werkzeug
        url_map = Map()
        for route in application.routes:
            # skip non string rules like 404. These should be handled by exceptions
            if not route.rule.isnumeric():
                url_map.add(Rule(route.rule, endpoint=route.template_name))
        urls = url_map.bind_to_environ(request.environ)
        endpoint, args = urls.match()
        template_data['path'].add_placeholders(args)

        app_template = jinja_env.get_template(endpoint)
        page_content = app_template.render(**template_data)
        app.record_transfer(page_content)
        return page_content

    except NotFound as e:
        # find the template for a 404 handler if specified
        for route in application.routes:
            if route.rule == '404':
                app_template = jinja_env.get_template(route.template_name)
                not_found_page = app_template.render(**template_data)
                app.record_transfer(not_found_page)
                return not_found_page, 404
        return '404', 404

    except Exception as e:
        return '500 internal error', 500


