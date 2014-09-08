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
                  'www1.%s' % DOMAIN_SUFFIX_BARE,
                  'dev.%s' % DOMAIN_SUFFIX_BARE]

# for api blueprint
CORS_SOURCE = ['*']

# host and cache are different DBs
REDIS_STORE_HOST = '127.0.0.1'
REDIS_STORE_PORT = 6379
REDIS_STORE_AUTH = ''
REDIS_STORE_DB = 0

MANDRILL_API_KEY = ''

TEMPLATE_GLOBAL_DEPLOYMENT = ''

STRIPE_SECRET_KEY = ''

class BaseConfig(object):

    SERVER_NAME = DOMAIN_SUFFIX_BARE
    SECRET_KEY = ''
    DEBUG = True
    MAX_CONTENT_LENGTH = (1024 ** 2) * 100
    SQLALCHEMY_DATABASE_URI = ''
    #SQLALCHEMY_ECHO = True


