from flask.ext.sqlalchemy import SQLAlchemy
import redis

import stripelib

from config import config


db = SQLAlchemy()
rds = redis.StrictRedis(host=config.REDIS_STORE_HOST, 
                        port=config.REDIS_STORE_PORT,
                        db=config.REDIS_STORE_DB,
                        password=config.REDIS_STORE_AUTH)

stripelib.api_key = config.STRIPE_SECRET_KEY
