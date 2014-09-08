import base64
import json
import os.path

from flask import current_app, request, g
from sqlalchemy.exc import SQLAlchemyError
import markdown
import scss
import yaml

from application.api.exception import APIError
from application.api.view import api_reply, check_signature
from application.blueprint import api as bp
from model import Account, AccountUser, ApplicationStaticContent, \
                  ApplicationStaticFile, ApplicationRoute, \
                  ApplicationTemplate, Application, Plan
import service
from service import mailer
from server_global import config, db


@bp.route('/beta-account/', versions=[0], methods=['POST'])
@api_reply
def create_beta_account():
    error = False
    errors = []
    flash = errors.append

    if len(request.form.get('application')) < 4 or \
       not service.valid_subdomain(request.form.get('application')):
        flash(
            'Account name must be at least 4 characters with alpha '
            'numeric and hyphen characters. It cannot start or end '
            'with a hyphen or have two or more consecutive hyphens.'
        )
        error = True
    if len(request.form.get('username')) < 6 or \
       len(request.form.get('password')) < 6:
        flash('Username and password both must be at least 6 characters')
        error = True
    if not service.valid_email(request.form.get('email')):
        flash('E-mail address is not valid')
        error = True
    if not error:
        plan = db.session.query(Plan).\
            filter(Plan.code_name=='beta open').one()
        user = AccountUser(
            username=request.form.get('username'),
            password=service.make_hash(request.form.get('password')),
            email=request.form.get('email')
        )
        account = Account(
            name=request.form.get('application'),
            users=[user]
        )
        account.inherit_plan(plan)
        db.session.add(account)
        db.session.commit()
        manager_uri = 'http://%s.%s/login/?first_registration=true' % (
            request.form.get('application'), 
            config.DOMAIN_SUFFIX_MANAGER
        )
        mailer.beta_registration(
            request.form.get('application'),
            request.form.get('username'),
            request.form.get('email')
        )
        reply = {'redirect': manager_uri}
    else:
        raise APIError(errors)
    return reply


@bp.route('/application/<application_name>/', versions=[0], methods=['PUT'])
@api_reply
@check_signature
def application(application_name):
    if application_name != g.account.name:
        raise APIError('Application specified not allowed for provided API '
                       'credentials')
    try:

        if g.account.application is not None:
            db.session.\
                query(Application).\
                filter(Application.id==g.account.application.id).\
                delete()

        application = Application()
        # first check the upload is not over any account limit
        # size limits are to be determined after base64 decoding, so those are
        # handled further into this API call
        data = json.loads(request.data)

        max_static_size = 0
        total_app_size = 0

        # fresh resources
        content_resources = {}
        template_sources = {}
        for category in ('content', 'static', 'templates'):
            values = data.get(category, {})
            for resource_key, rawdata in values.iteritems():
                extension = os.path.splitext(resource_key)[1]
                binary_data = base64.b64decode(rawdata)
                total_app_size += len(binary_data)

                # precompiling data files into python dicts
                if category == 'content':
                    resource = ApplicationStaticContent()
                    resource.resource_key = resource_key
                    if extension == '.yaml':
                        native_data = yaml.load(binary_data)
                    elif extension == '.json':
                        native_data = json.loads(binary_data)
                    else:
                        native_data = {}
                    resource.data = json.dumps(native_data)
                    application.static_contents.append(resource)
                    content_resources[resource_key] = resource

                # static data is just a blob
                elif category == 'static':
                    # SCSS "sassy css"
                    if resource_key.startswith('css/') and \
                       resource_key.endswith('.scss'):
                        _scss = scss.Scss()
                        css_data = _scss.compile(binary_data)
                        static_data = css_data

                    # stylus
                    elif resource_key.startswith('css/') and \
                       resource_key.endswith('.styl'):
                        static_data = service.compile_stylus(binary_data)

                    # less 
                    elif resource_key.startswith('css/') and \
                       resource_key.endswith('.less'):
                        static_data = service.compile_less(binary_data)

                    # coffee script
                    elif resource_key.startswith('js/') and \
                       resource_key.endswith('.coffee'):
                        js_data = service.compile_coffeescript(binary_data)
                        static_data = js_data

                    else:
                        static_data = binary_data

                    max_static_size = max(max_static_size, len(static_data))
                    resource = ApplicationStaticFile()
                    resource.resource_key = resource_key
                    resource.data = static_data
                    application.static_files.append(resource)

                # template processing
                elif category == 'templates':

                    # markdown to straight HTML
                    if resource_key.endswith('.md'):
                        jinja2 = markdown.markdown(binary_data)

                    # everything else for jinja2
                    else:
                        jinja2 = service.preprocess_jade(
                            binary_data, resource_key)

                    template = ApplicationTemplate()
                    template.key = resource_key
                    template.jinja2 = jinja2
                    application.templates.append(template)

        # fresh routes
        app_yaml = base64.b64decode(data.get('application_config', ''))
        total_app_size += len(app_yaml)
        app_data = yaml.load(app_yaml)
        routes = app_data.get('routes', [])
        for route in routes:
            app_route = ApplicationRoute()
            app_route.rule = route['rule']
            app_route.template_name = route['template']
            app_route.static_contents = []
            if 'content' in route:
                if isinstance(route['content'], str):
                    route_content = [route['content']]
                else:
                    route_content = route['content']

                for data_resource in route_content:
                    app_route.static_contents.append(content_resources[data_resource])
            application.routes.append(app_route)

        application.account = g.account
        db.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        raise
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        raise APIError(e)
    return {'name': g.account.name}


