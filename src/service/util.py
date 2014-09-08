import base64
from datetime import datetime, timedelta
import hashlib
import hmac
import os
import os.path
import re
import uuid as uuidlib
import StringIO
import subprocess
import sys
import tempfile
from types import StringTypes
from pytz import timezone as timez

import bcrypt
import dns.resolver
from flask import get_flashed_messages, request, render_template, url_for
import markdown as markdownlib
from pyjade.utils import process as jade_process
from pyjade.ext.jinja import Compiler as JadeCompiler

from server_global import config


class AppTemplateRegistrar(object):
    '''
    Helper class to quickly add views for a flask app
    usage:  
        registrar = AppTemplateRegistrar(app)
        registrar.register('/', 'home', 'home.jade')
    '''

    def __init__(self, app):
        self.app = app

    def register(self, route, endpoint, template):
        self.app.add_url_rule(route, endpoint, self.view_func(template))

    def view_func(self, template):
        def view():
            return render_template(template)
        return view


def api_signature(secret, req):
    verb = req.method
    content = req.data
    content_hash = sha1(content).hexdigest()
    date = req.headers.get('Date')
    uri = '/' + req.url.split('/', 3)[-1]
    if date is None:
        raise Error
    msg = '\n'.join([verb, content_hash, date, uri])
    signer = hmac.new(secret, msg, hashlib.sha1)
    signature = signer.digest()
    signature64 = base64.b64encode(signature)
    return signature64
    

def sha1(content):
    hasher = hashlib.sha1()
    hasher.update(content)
    return hasher


def is_app_domain(domain=None):
    if domain is None:
        uri_parts = request.url.split('/')
        domain = uri_parts[2].split(':')[0] # remove potential port numbers
    is_app = domain.endswith(config.DOMAIN_SUFFIX_APP)
    return is_app


def is_muh_domain(domain=None):
    if domain is None:
        uri_parts = request.url.split('/')
        domain = uri_parts[2].split(':')[0] # remove potential port numbers
    is_muh = domain.endswith(config.DOMAIN_SUFFIX_BARE) and \
        domain not in config.DOMAIN_DOGFOOD
    return is_muh


def is_custom_domain(domain):
    return is_app


def extract_domain(uri):
    '''gets domain from full uri address'''
    if uri is None:
        return None
    uri_parts = uri.split('/')
    domain = uri_parts[2].split(':')[0] # remove potential port numbers
    return domain


def feign_hash(complexity=13):
    salt = bcrypt.gensalt(complexity)
    bcrypt.hashpw(os.urandom(10), salt)


def make_hash(string, complexity=13):
    salt = bcrypt.gensalt(complexity)
    hash_pw = bcrypt.hashpw(string, salt)
    return hash_pw
    

def verify_hash(password, password_hash):
    hash_pw = bcrypt.hashpw(password, password_hash)
    match = hash_pw == password_hash
    return match


def uuid():
    return uuidlib.uuid4()


def get_flashes(category):
    return get_flashed_messages(True, [category])


def valid_email(email):
    if email.count('@') != 1 or email[0] == '@' or email[-1] == '@':
        return False
    parts = email.split('@')
    if parts[1][0] == '.' or parts[1][-1] == '.':
        return False
    return True


def valid_subdomain(subdomain):
    start = subdomain[0]
    end = subdomain[-1]
    if start == '-' or end == '-' or '--' in subdomain:
        return False
    parts = subdomain.split('-')
    for part in parts:
        if not part.isalnum():
            return False
    return True


def url_builder_manager(error, endpoint, values):
    '''
    url_builder for manager

    Since the manager blueprint has the <application>.manager subdomain,
    url_for needs that parameter passed explicitly. But it's a pain, so if
    it is not passed, an error will be passed, and this function will then
    handle it correctly by adding in the parameter automatically.

    There is also functionality needed when custom domains are allowed for
    the manager.

    '''
    if request.blueprint in ('manager', 'cms') and 'application' not in values:
        domain = request.url.split('/')[2]
        parts = domain.split('.')
        application = parts[-4]
        values['application'] = application
        return url_for(endpoint, **values)
    else:
        raise error


def server_path(*args):
    '''
    returns server src path with additional joined directories
    '''
    src_path = os.path.abspath(sys.path[0])
    server_path = os.path.join(src_path, *args)
    return server_path


def url_values_manager(endpoint, kwargs):
    '''
    application is prepopulated by the blueprint so it can serve app 
    subdomains. This makes sure it is removed from the view so every view
    doesn't need that as a parameter.
    '''
    if 'application' in kwargs:
        del kwargs['application']


def compile_coffeescript(source):
    '''
    compiles coffeescript source into javascript

    uses the node binary with the --stdio to use stdin and stdout
    '''
    try:
        command = ['coffee-script', 'bin', 'coffee']
        args = ['--stdio', '--print']
        js_source = node_command_in(command, args, source)
        return js_source
    except:
        raise Exception('Coffeescript compilation error')


def compile_less(source):
    try:
        command = ['less', 'bin', 'lessc']
        args = ['-']
        css_source = node_command_in(command, args, source)
        return css_source
    except:
        raise Exception('Less CSS compilation error')


def compile_stylus(source):
    try:
        command = ['stylus', 'bin', 'stylus']
        css_source = node_command_in(command, stdin=source)
        return css_source
    except:
        raise Exception('Stylus CSS compilation error')


def node_command(command, args=[], **proc_kw):
    node = server_path('node', 'node')
    command = server_path('node', *command)
    cmd_args = [node, command] + args
    results = subprocess.check_output(cmd_args, **proc_kw)
    return results


def node_command_in(command, args=[], stdin=''):
    '''node_command with stdin support'''
    infile = tempfile.TemporaryFile()
    infile.write(stdin)
    infile.seek(0)
    results = node_command(command, args, stdin=infile)
    return results


def preprocess_jade(source, name='unnamed.jade'):
    '''convert jade source string into jinja2'''
    results = jade_process(source, filename=name, compiler=JadeCompiler)
    return results


def dns_cname(domain):
    '''
    query google DNS and look for CNAME entries
    '''
    try:
        dns_resolver = dns.resolver.Resolver()
        dns_resolver.nameservers = config.DNS_SOURCES
        response = dns_resolver.query(domain)
        answers = response.response.answer
        fqsource = domain + '.'
        for line in answers:
            t = line.to_text()
            if t.startswith(fqsource) and ' IN CNAME ' in t:
                # -1 end to remove trailing period
                source = domain
                destination = t.split(' IN CNAME ')[1][:-1]
                ttl = line.ttl
                return (source, destination, ttl)
        return None
    except:
        return None


def timestamp_boundaries(timestamp_l, timezone):
    '''
    returns two datetime objects that are inclusive boundaries defined by the
    parameters.


    timestamp is an list that can get finer in granularity: 
    [year, month, day, hour, minute, second]
    ex. if only year and month is specified, it will assume range wanted 
    includes any day.
    '''
    timestamp = [int(t) for t in timestamp_l]
    depth = len(timestamp)

    while len(timestamp) < 3:
        timestamp.append(1)
    while len(timestamp) < 6:
        timestamp.append(0)

    if len(timestamp) > 6:
        timestamp = timestamp[:6]
    timestamp.append(0)

    tz = timez(timezone)

    lower = datetime(*timestamp, tzinfo=tz)

    # one more year
    if depth == 1:
        timestamp[0] += 1
    # one more month, check for month 12 overage
    elif depth == 2:
        if timestamp[1] == 12:
            timestamp[0] += 1
            timestamp[1] = 1
        else:
            timestamp[1] += 1

    higher = datetime(*timestamp, tzinfo=tz)

    # one more day, user timedelta from here and more granular levels
    if depth == 3:
        higher += timedelta(days=1)
    # one more hour
    elif depth == 4:
        higher += timedelta(hours=1)
    # one more minute
    elif depth == 5:
        higher += timedelta(minutes=1)
    # one more second
    elif depth == 6:
        higher += timedelta(seconds=1)

    return (lower, higher)


def markdown(string=''):
    '''safer markdown'''
    try:
        return markdownlib.markdown(string)
    except:
        return ''
