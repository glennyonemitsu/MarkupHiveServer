import datetime

from sqlalchemy.orm.exc import NoResultFound

from server_global import db


class Plan(db.Model):
    '''
    Account plan reference

    Not directly referenced in foreign keys. Copied instead for further 
    customization.
    '''

    id = db.Column(db.Integer, primary_key=True)
    code_name = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Numeric(5, 2))
    available = db.Column(db.Boolean)
    custom_domain = db.Column(db.Boolean)
    cms = db.Column(db.Boolean)
    size_total = db.Column(db.Integer, nullable=True)
    size_static = db.Column(db.Integer, nullable=True)
    transfer = db.Column(db.Integer, nullable=True)
    count_template = db.Column(db.Integer, nullable=True)
    count_static = db.Column(db.Integer, nullable=True)
