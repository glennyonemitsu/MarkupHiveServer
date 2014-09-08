import base64
from datetime import datetime, timedelta
import hashlib
import json
import os

from sqlalchemy.orm.exc import NoResultFound 

from server_global import db, rds
import service
from service import app


association_application_route_content = db.Table(
    'association_application_route_content', 
    db.metadata,
        db.Column('route_id', db.BigInteger, db.ForeignKey('application_route.id')),
        db.Column('content_id', db.BigInteger, db.ForeignKey('application_static_content.id'))
)


class Application(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    routes = db.relationship('ApplicationRoute', backref='application')
    templates = db.relationship('ApplicationTemplate', backref='application')
    static_files = db.relationship('ApplicationStaticFile', backref='application')
    static_contents = db.relationship('ApplicationStaticContent', backref='application')

    @classmethod
    def get_by_name(cls, name):
        try:
            return db.session.query(cls).filter(cls.name==name).one()
        except NoResultFound:
            return None


class ApplicationRoute(db.Model):
    
    __tablename__ = 'application_route'

    id = db.Column(db.BigInteger, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    rule = db.Column(db.String(255))
    template_name = db.Column(db.String(255))
    static_contents = db.relationship(
        'ApplicationStaticContent', 
        secondary=association_application_route_content,
        backref='routes'
    )


class ApplicationTemplate(db.Model):
    
    __tablename__ = 'application_template'

    id = db.Column(db.BigInteger, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    key = db.Column(db.String(255), nullable=False)
    jinja2 = db.Column(db.Text)


class ApplicationStaticFile(db.Model):
    
    __tablename__ = 'application_static_file'

    id = db.Column(db.BigInteger, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    resource_key = db.Column(db.String(255))
    data = db.Column(db.BLOB)


class ApplicationStaticContent(db.Model):
    
    __tablename__ = 'application_static_content'

    id = db.Column(db.BigInteger, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    resource_key = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text)


