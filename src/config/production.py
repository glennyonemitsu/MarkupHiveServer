AWS_ACCESS_KEY = ''
AWS_SECRET_ACCESS_KEY = '+LpVnq79iXzmBpx0'

DEPLOYMENT = ''

# for custom domains
DNS_SOURCES = ['']

DOMAIN_SUFFIX_BARE = ''
DOMAIN_SUFFIX_APP = ''
DOMAIN_SUFFIX_MANAGER = ''

# list of domains to skip serving because we will dog food our own hosting 
# service
DOMAIN_DOGFOOD = ['www.%s' % DOMAIN_SUFFIX_BARE,
                  'dev.%s' % DOMAIN_SUFFIX_BARE]

# for api blueprint
CORS_SOURCE = [
    'www.%s' % DOMAIN_SUFFIX_BARE,
    'markuphive.%s' % DOMAIN_SUFFIX_APP ]
CORS_SOURCE = ['*']

# host and cache are different DBs
REDIS_STORE_HOST = '127.0.0.1'
REDIS_STORE_PORT = 6666 # local redis instance
REDIS_STORE_DB = 0

MANDRILL_API_KEY = ''

TEMPLATE_GLOBAL_DEPLOYMENT = ''

STRIPE_SECRET_KEY = ''

class BaseConfig(object):

    SERVER_NAME = ''
    SECRET_KEY = ''
    DEBUG = False
    MAX_CONTENT_LENGTH = (1024 ** 2) * 100
    SQLALCHEMY_DATABASE_URI = ''


