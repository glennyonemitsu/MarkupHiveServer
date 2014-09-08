from collections import OrderedDict
from datetime import datetime
from types import StringTypes

from flask.ext.wtf import Form
from pytz import common_timezones, timezone as timez
from sqlalchemy.orm.exc import NoResultFound 
from sqlalchemy.dialects.postgresql import ARRAY, UUID, HSTORE, VARCHAR, Any, array
from sqlalchemy.sql.expression import cast, func
from wtforms.fields import TextField, SubmitField, SelectField
from wtforms.validators import DataRequired as Required
from wtforms.widgets import ListWidget

from server_global import db
import service
from form.manager.cms_field_type import field_types


class ContentType(db.Model):

    __tablename__ = 'content_type'

    uuid = db.Column(UUID, primary_key=True)
    order = db.Column(db.Integer)
    name = db.Column(db.String(100))
    description = db.Column(db.String(250))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'))

    entries = db.relationship(
        'ContentEntry', 
        backref='content_type',
        order_by='ContentEntry.timestamp')

    field_groups = db.relationship(
        'ContentFieldGroup', 
        cascade='delete',
        backref='content_type',
        order_by='ContentFieldGroup.order')

    statuses = db.relationship(
        'ContentTypeStatus', 
        cascade='delete',
        backref='content_type',
        order_by='ContentTypeStatus.order')

    @property
    def status_options(self):
        statuses = [(row.uuid, row.name) for row in self.statuses]
        return statuses


    @property
    def entry_form(self):
        '''
        create an entry form for manager use
        '''
        if not hasattr(self, 'form'):
            class_name = 'ContentEntryForm'
            class_parents = (Form,)
            attributes = {}

            form = type(class_name, (Form,), {})

            title_field = TextField('Title', [Required('Title is required')])
            title_field.bind(form, 'content_entry_title')
            setattr(form, 'content_entry_title', title_field)
            slug_field = TextField('Slug', [Required('Slug is required')])
            slug_field.bind(form, 'content_entry_slug')
            setattr(form, 'content_entry_slug', slug_field)

            tag_field = TextField('Tags')
            tag_field.bind(form, 'content_entry_tag')
            setattr(form, 'content_entry_tag', tag_field)

            status_field = SelectField('Status', choices=self.status_options)
            status_field.bind(form, 'content_entry_status')
            setattr(form, 'content_entry_status', status_field)

            save_field = SubmitField('Save')
            save_field.bind(form, 'content_entry_save')
            setattr(form, 'content_entry_save', save_field)

            delete_field = SubmitField('Delete')
            delete_field.bind(form, 'content_entry_delete')
            setattr(form, 'content_entry_delete', delete_field)

            field_groups = []
            for group in self.field_groups:
                if group.fields:
                    field_group = {'uuid': group.uuid,
                                   'name': group.name,
                                   'fields': []}
                    for field in group.fields:
                        form_field = field.field(field.name)
                        form_field.bind(form, field.name)
                        setattr(form, field.name, form_field)

                        field_group['fields'].append(field.name)
                    field_groups.append(field_group)
            attributes['_field_groups'] = field_groups
            self.form = form
            self.form._field_groups = field_groups
        return self.form
    
    def entries_query(self, page=0, limit=10, tags=[], timestamp=[], timezone='UTC', status='Published'):
        page = int(page)
        limit = int(limit)
        offset = page * limit

        # tags, timestamps, and status can be comma delimited or lists
        if type(tags) in StringTypes:
            tags = tags.split(',')
            if tags == ['']:
                tags = []
        tags = list(tags)
        if type(timestamp) in StringTypes:
            timestamp = timestamp.split(',')
            if timestamp == ['']:
                timestamp = []
        timestamp = list(timestamp)
        if type(status) in StringTypes:
            status = status.split(',')
            if status == [''] or status == ['*']:
                status = []
        status = list(status)

        query = db.session.\
            query(ContentEntry).\
            filter(ContentEntry.content_type_uuid==self.uuid)

        if tags:
            query = query.filter( 
                ContentEntry.tag.overlap(cast(tags, ARRAY(VARCHAR(20))))
            )

        if timezone not in common_timezones:
            timezone = 'UTC'

        if timestamp:
            lower, higher = service.timestamp_boundaries(timestamp, timezone)
            query = query.filter(ContentEntry.timestamp >= lower,
                                 ContentEntry.timestamp < higher)

        if status:
            query = query.\
                join(ContentEntry.status).\
                filter(ContentTypeStatus.name.in_(status))

        query = query.\
            order_by(ContentEntry.timestamp.desc()).\
            offset(offset).\
            limit(limit)

        rows = query.all()
        entries = [row.app_data(timezone) for row in rows]
        return entries

    def entries_query_count(self, tags=[], timestamp=[], timezone='UTC', status='Published'):

        # tags, timestamps, and status can be comma delimited or lists
        if type(tags) in StringTypes:
            tags = tags.split(',')
            if tags == ['']:
                tags = []
        tags = list(tags)
        if type(timestamp) in StringTypes:
            timestamp = timestamp.split(',')
            if timestamp == ['']:
                timestamp = []
        timestamp = list(timestamp)
        if type(status) in StringTypes:
            status = status.split(',')
            if status == [''] or status == ['*']:
                status = []
        status = list(status)

        query = db.session.\
            query(func.count(ContentEntry.uuid)).\
            filter(ContentEntry.content_type_uuid==self.uuid)

        if tags:
            query = query.filter( 
                ContentEntry.tag.overlap(cast(tags, ARRAY(VARCHAR(20))))
            )

        if timestamp:
            if timezone not in common_timezones:
                timezone = 'UTC'
            lower, higher = service.timestamp_boundaries(timestamp, timezone)
            query = query.filter(ContentEntry.timestamp >= lower,
                                 ContentEntry.timestamp < higher)

        if status:
            query = query.\
                join(ContentEntry.status).\
                filter(ContentTypeStatus.name.in_(status))

        return query.scalar()


class ContentTypeStatus(db.Model):

    __tablename__ = 'content_type_status'

    uuid = db.Column(UUID, primary_key=True)
    content_type_uuid = db.Column(UUID, db.ForeignKey('content_type.uuid', ondelete='CASCADE'))
    order = db.Column(db.Integer)
    name = db.Column(db.String(30))


class ContentFieldGroup(db.Model):

    __tablename__ = 'content_field_group'

    uuid = db.Column(UUID, primary_key=True)
    order = db.Column(db.Integer)
    name = db.Column(db.String(100))
    content_type_uuid = db.Column(UUID, db.ForeignKey('content_type.uuid', ondelete='CASCADE'))

    fields = db.relationship(
        'ContentField', 
        cascade='delete',
        backref='field_group',
        order_by='ContentField.order')


class ContentField(db.Model):
    
    __tablename__ = 'content_field'

    uuid = db.Column(UUID, primary_key=True)
    order = db.Column(db.Integer)
    name = db.Column(db.String(100))
    type_key = db.Column(db.String(40))

    content_field_group_uuid = db.Column(UUID, db.ForeignKey('content_field_group.uuid', ondelete='CASCADE'))
    content_type_uuid = db.Column(UUID, db.ForeignKey('content_field_type.uuid', ondelete='CASCADE'))

    field_types = field_types

    @property
    def label(self):
        return self.field_types[self.type_key]['label']

    @property
    def field(self):
        return self.field_types[self.type_key]['field']

class ContentFieldType(db.Model):
    
    __tablename__ = 'content_field_type'

    uuid = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(100))


class ContentEntry(db.Model):
    
    __tablename__ = 'content_entry'

    uuid = db.Column(UUID, primary_key=True)
    content_type_uuid = db.Column(UUID, db.ForeignKey('content_type.uuid'))
    current_revision_uuid = db.Column(UUID, db.ForeignKey('content_revision.uuid', ondelete='SET NULL'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'))
    title = db.Column(db.String(200))
    slug = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime(True), default=datetime.now)
    tag = db.Column(ARRAY(VARCHAR(20)))
    content_type_status_uuid = db.Column(UUID, db.ForeignKey('content_type_status.uuid'))

    status = db.relationship(
        'ContentTypeStatus',
        foreign_keys='ContentEntry.content_type_status_uuid')

    account = db.relationship(
        'Account',
        foreign_keys='ContentEntry.account_id')

    revision = db.relationship(
        'ContentRevision', 
        foreign_keys='ContentEntry.current_revision_uuid')

    @classmethod
    def find_by_uuid(cls, uuid, status='Published'):
        try:
            if type(status) in StringTypes:
                status = status.split(',')
                if status == [''] or status == ['*']:
                    status = []
            status = list(status)

            query = db.session.query(cls).filter(cls.uuid==uuid)
            if status:
                query = query.\
                    join(ContentTypeStatus).\
                    filter(ContentTypeStatus.name.in_(status))
            entry = query.one()
            return entry
        except:
            return None

    @classmethod
    def find_by_slug(cls, slug, status='Published'):
        try:
            if type(status) in StringTypes:
                status = status.split(',')
                if status == [''] or status == ['*']:
                    status = []
            status = list(status)

            query = db.session.query(cls).filter(cls.slug==slug)
            if status:
                query = query.\
                    join(ContentTypeStatus).\
                    filter(ContentTypeStatus.name.in_(status))
            entry = query.one()
            return entry
        except:
            return None

    @property
    def form_data(self):
        '''
        prepare the data for the entry form in the manager
        '''
        data = self.revision.field_data
        data['content_entry_title'] = self.title
        data['content_entry_slug'] = self.slug
        data['content_entry_tag'] = self.tag
        data['content_entry_status'] = self.content_type_status_uuid
        return data

    def app_data(self, timezone):
        '''
        dict object with data for app jade template
        '''
        data = self.revision.field_data
        data['_uuid'] = self.uuid
        data['_title'] = self.title
        data['_slug'] = self.slug
        data['_tags'] = [] if self.tag is None else self.tag
        data['_status'] = self.status.name

        if timezone not in common_timezones:
            timezone = 'UTC'
        tz = timez(timezone)
        o_timestamp = self.timestamp.astimezone(tz)
        r_timestamp = self.revision.timestamp.astimezone(tz)

        # original timestamp
        data['_year'] = o_timestamp.year
        data['_month'] = o_timestamp.month
        data['_day'] = o_timestamp.day
        data['_hour'] = o_timestamp.hour
        data['_minute'] = o_timestamp.minute
        data['_second'] = o_timestamp.second
        data['_ampm'] = o_timestamp.strftime('%p').lower()
        data['_AMPM'] = o_timestamp.strftime('%p').upper()
        data['_timezone'] = o_timestamp.strftime('%z')

        data['_hour12'] = int(o_timestamp.strftime('%I'))
        data['_hour24'] = o_timestamp.hour

        # revision timestamp
        data['_year_r'] = r_timestamp.year
        data['_month_r'] = r_timestamp.month
        data['_day_r'] = r_timestamp.day
        data['_hour_r'] = r_timestamp.hour
        data['_minute_r'] = r_timestamp.minute
        data['_second_r'] = r_timestamp.second
        data['_ampm_r'] = r_timestamp.strftime('%p').lower()
        data['_AMPM_r'] = r_timestamp.strftime('%p').upper()
        data['_timezone_r'] = r_timestamp.strftime('%z')

        data['_hour12_r'] = int(r_timestamp.strftime('%I'))
        data['_hour24_r'] = r_timestamp.hour

        return data

class ContentRevision(db.Model):
    
    __tablename__ = 'content_revision'

    uuid = db.Column(UUID, primary_key=True)
    content_entry_uuid = db.Column(UUID, db.ForeignKey('content_entry.uuid'))
    account_user_id = db.Column(db.Integer, db.ForeignKey('account_user.id', ondelete='SET NULL'))
    timestamp = db.Column(db.DateTime(True), default=datetime.now)
    field_data = db.Column(HSTORE)

        

    #entry = db.relationship(
        #'ContentEntry', 
        #back_populates='revisions',
        #foreign_keys='ContentRevision.content_entry_uuid')
