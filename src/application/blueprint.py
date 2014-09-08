from flask import Blueprint, g, url_for

from service import get_flashes


class APIBlueprint(Blueprint):

    def route(self, rule, versions, **options):
        '''
        works just like the original route decorator but registers for 
        multiple prefixes based on the version parameter.

        Endpoints get a _# appended to the name. The unedited endpoint name
        will reference the max version uri.
        '''
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            for version in versions:
                # assumes rules start with a /
                vrule = '/v{version}{rule}'.format(
                    version=version,
                    rule=rule)

                vendpoint = '{endpoint}_{version}'.format(
                    endpoint=endpoint,
                    version=version)

                self.add_url_rule(vrule, vendpoint, f, **options)
            
            # higest versioned url prefix is for vanilla endpoint name
            mrule = '/v{version}{rule}'.format(
                version=max(versions),
                rule=rule)
            self.add_url_rule(mrule, endpoint, f, **options)
            return f
        return decorator


# non-public blueprints
admin = Blueprint(
    'admin', 'application', subdomain='nerv',
    template_folder='template', 
    static_folder='static/admin',
    static_url_path='/static',
)

manager = Blueprint(
    'manager', 'application', subdomain='<application>.manager',
    template_folder='template', 
    static_folder='static/manager',
    static_url_path='/static',
)
cms = Blueprint(
    'cms', 'application', subdomain='<application>.manager',
    template_folder='template', 
    static_folder='static/manager',
    static_url_path='/static',
    url_prefix='/cms',
)

app = Blueprint(
    'app', 'application', subdomain='<application>.app'
)

api = APIBlueprint('api', 'application', subdomain='api')


# context processors
@admin.context_processor
def admin_context():
    return {'get_flashes': get_flashes,
            'u': url_for,}


@manager.context_processor
@cms.context_processor
def manager_context():
    return {'g': g,
            'account': g.account,
            'get_flashes': get_flashes,
            'u': url_for,}
