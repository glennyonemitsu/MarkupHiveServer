import base64
from datetime import datetime, timedelta
import hashlib
import json
import os

from sqlalchemy.orm.exc import NoResultFound 

from model.application import Application
from server_global import db, rds
import service
from service import app


class Account(db.Model):

    __table_name__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    canonical_domain = db.Column(db.String(250), nullable=True)

    api_keys = db.relationship('AccountAPIKey', backref='account')
    users = db.relationship('AccountUser', backref='account')
    applications = db.relationship('Application', backref='account')

    # cms relations
    content_types = db.relationship('ContentType', 
                                    order_by='ContentType.order',
                                    backref='account')

    plan_name = db.Column(db.String(200))
    plan_code_name = db.Column(db.String(200))
    custom_domain = db.Column(db.Boolean)
    price = db.Column(db.Numeric(5, 2))
    cms = db.Column(db.Boolean)
    size_total = db.Column(db.Integer)
    size_static = db.Column(db.Integer)
    transfer = db.Column(db.Integer)
    count_template = db.Column(db.Integer)
    count_static = db.Column(db.Integer)
    join_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def application(self):
        '''
        When multiple application instances (uploaded versions) are enabled
        this will come in handy to do a "current application" lookup
        '''
        try:
            return self.applications[0]
        except:
            return None

    def add_api_key(self):
        new_key = AccountAPIKey()
        new_key.access_key = AccountAPIKey.unique_key()
        new_key.secret = os.urandom(32)
        self.api_keys.append(new_key)

    def get_api_key(self, access_key):
        for api_key in self.api_keys:
            if api_key.access_key == access_key:
                return api_key
        return None

    def delete_api_key(self, access_key):
        for api_key in self.api_keys:
            if api_key.access_key == access_key:
                key = self.api_keys.index(api_key)
                del self.api_keys[key]

    def inherit_plan(self, plan):
        '''
        Transfer all the plan fields to this record
        '''
        # field names of the Plan model
        fields = ['code_name', 'name', 'custom_domain', 'price', 'cms', 
                  'size_total', 'size_static', 'transfer', 'count_template', 
                  'count_static']
        for field in fields:
            value = getattr(plan, field)
            if field in ('code_name', 'name'):
                field = 'plan_' + field
            setattr(self, field, value)

    def monthly_transfer_total(self, year, month):
        '''
        Get the application's monthly data transfer usage.

        Default to 0
        '''
        key = 'xferm:{app_id}'.format(app_id=self.id)
        field = '{year}{month}'.format(year=year, month=month)
        xfer = rds.hget(key, field)
        xfer = int(xfer) if xfer is not None else 0
        return xfer

    def monthly_transfer_daily(self, year, month):
        '''
        Get the application's daily data transfer usage for a given month.

        If day was never recorded (past, present, or future) it will convert
        that days value to 0
        '''
        key = 'xferd:{app_id}'.format(app_id=self.id)
        field_fmt = '{year}{month}{day}'
        fields = [
            field_fmt.format(year=year, month=month, day=str(day).zfill(2)) \
            for day in range(1, 32)
        ]
        days = rds.hmget(key, fields)
        xfer = [int(day) if day is not None else 0 for day in days]
        return xfer

    def record_transfer(self, size):
        app.record_transfer(size, self.id)

    @classmethod
    def get_by_name(cls, name):
        try:
            return db.session.query(cls).filter(cls.name==name).one()
        except Exception as e:
            return None


class AccountAPIKey(db.Model):

    __tablename__ = 'account_api_key'

    id = db.Column(db.BigInteger, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    access_key = db.Column(db.String(24), unique=True)
    secret = db.Column(db.BINARY(32))

    @classmethod
    def unique_key(cls):
        while True:
            try:
                sha = hashlib.sha1()
                k = os.urandom(200)
                sha.update(k)
                key = sha.hexdigest()[:24]
                db.session.query(cls).filter(cls.access_key==key).one()
            except NoResultFound:
                return key

    def secret64(self):
        return base64.b64encode(self.secret)


class AccountUser(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(255))

    def valid_password(self, password):
        return service.verify_hash(password, self.password)


