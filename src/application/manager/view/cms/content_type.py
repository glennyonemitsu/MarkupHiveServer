import json

from flask import g, flash, make_response, redirect, render_template, \
                  request, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from application.blueprint import cms as bp
from form.manager.cms import ContentTypeForm, FieldTypeForm
from form.manager.cms_field_type import field_types
from model.cms import ContentType, ContentFieldGroup, ContentField, \
                      ContentEntry, ContentRevision
from server_global import db

from service import app_cms as cms


def uuid_check(fn):
    '''
    decorator to check logged in account's content type uuids
    
    if found, continues the call chain and adds 'ctype' kwarg with ContentType
    record.

    Lookup sources are uuid in url, then content_type_uuid in POST
    '''
    def check(*args, **kwargs):
        ctype = None
        uuid = kwargs.get('uuid', request.form.get('content_type_uuid'))
        for ct in g.account.content_types:
            if ct.uuid == uuid:
                ctype = ct
                break
        if ctype is None:
            return {'error': ['The content type does not exist'],
                    'success': False}
        else:
            kwargs['uuid'] = uuid
            kwargs['ctype'] = ctype
            return fn(*args, **kwargs)
    check.__name__ = fn.__name__
    return check


def api(fn):
    '''decorator to return json strings from return values'''
    def jsonify(*args, **kwargs):
        result = fn(*args, **kwargs)
        json_response = json.dumps(result)
        res = make_response(json_response)
        res.headers['Content-type'] = 'application/json'
        return res
    jsonify.__name__ = fn.__name__
    return jsonify


@bp.route('/content-types/')
def content_type_list():
    types = db.session.query(ContentType).\
        filter(ContentType.account_id==g.account.id).\
        order_by(ContentType.order).all()
    return render_template(
        'manager/cms/content-type-home.jade',
        title='Select content type to edit',
        types=types)


@bp.route('/content-type/create/', methods=['GET', 'POST'])
def content_type_create():
    form = ContentTypeForm(request.form)
    if request.method == 'POST' and form.validate():
        ctype_count = db.session.query(ContentType).count()
        
        ctype = ContentType()
        ctype.account_id = g.account.id
        ctype.order = ctype_count
        form.populate_obj(ctype)

        field_group = ContentFieldGroup()
        field_group.order = 0
        field_group.name = '{name} data'.format(name=ctype.name)

        ctype.field_groups = [field_group]

        db.session.add(ctype)
        db.session.add(field_group)
        db.session.commit()
        return redirect(url_for('cms.content_type_edit', uuid=ctype.uuid))

    return render_template(
        'manager/cms/content-type-create.jade',
        title='Create new content type',
        form=form)


@bp.route('/edit/<uuid:uuid>/')
def content_type_edit(uuid):
    try:
        ctype = db.session.query(ContentType).\
            filter(ContentType.uuid==str(uuid)).one()
    except:
        return redirect(url_for('cms.content_type_list'))
    title = 'Edit content type'
    return render_template(
        'manager/cms/content-type-edit.jade',
        type_form=FieldTypeForm(),
        field_types=field_types,
        title=title,
        ctype=ctype)


# API methods. Allows only POST or PUT and returns a json string
@bp.route('/content-type/<uuid>/', methods=['POST'])
@api
@uuid_check
def content_type_meta(uuid, ctype):
    action = request.form.get('action')
    if action == 'update':
        result = {'success': True}
        if not len(request.form.get('name')):
            result['notice'] = ['Content type name cannot be empty']
            result['success'] = False
        if len(request.form.get('description')) > 250:
            result['notice'] = ['Content type description cannot be more than 250 characters']
            result['success'] = False
        if result['success']:
            ctype.name = request.form.get('name')
            ctype.description = request.form.get('description')
            result['name'] = ctype.name
            result['description'] = ctype.description
            db.session.commit()
        return result
    elif action == 'delete':
        confirm_phrase = 'delete {name}'.format(name=ctype.name)
        try:
            if confirm_phrase == request.form.get('confirm_phrase'):
                db.session.delete(ctype)
                db.session.commit()
                return {'success': True}
            else:
                return {'success': False,
                        'notice': ['Confirmation phrase is not correct']}
        except Exception as e:
            return {'success': False,
                    'error': ['Server error']}
        

@bp.route('/field-group/', methods=['POST'])
@api
@uuid_check
def content_type_field_group(uuid, ctype):
    order = len(ctype.field_groups)
    group = ContentFieldGroup()
    group.order = order
    group.name = request.form.get('name')
    ctype.field_groups.append(group)
    try:
        db.session.add(group)
        db.session.commit()
        result = {
            'success': True,
            'uuid': group.uuid,
            'name': group.name
        }
    except IntegrityError:
        result = {
            'success': False,
            'notice': ['You cannot have duplicate field group names']
        }
    except Exception as e:
        result = {
            'success': False,
            'error': ['Server error']
        }
    return result


@bp.route('/field-group/<fg_uuid>/', methods=['POST'])
@api
@uuid_check
def content_type_field_group_edit(uuid, ctype, fg_uuid):
    fg = None
    for group in ctype.field_groups:
        if fg is None and group.uuid == fg_uuid:
            fg = group
    if fg is None:
        return {'success': False, 
                'notice': ['Field group UUID is not found for this content type']}
    action = request.form.get('action')
    if action == 'update':
        try:
            fg.name = request.form.get('name')
            db.session.commit()
            return {'success': True,
                    'field_group': {'uuid': fg.uuid,
                                    'name': fg.name,
                                    'order': fg.order}}
        except IntegrityError:
            return {'success': False,
                    'notice': ['You cannot have duplicate field group names']}
        except Exception as e:
            return {'success': False,
                    'error': ['Server error']}
    elif action == 'delete':
        try:
            # there is, now remove and loop through again to reorder
            field_group= {'uuid': fg.uuid,
                          'name': fg.name,
                          'order': fg.order}
            ctype.field_groups.remove(fg)
            db.session.delete(fg)
            # rewrite the ordering
            for i, group in enumerate(ctype.field_groups):
                group.order = i

            db.session.commit()
            return {'success': True,
                    'field_group': field_group}
        except Exception as e:
            return {'success': False,
                    'error': ['Server error']}
    elif action.startswith('shift-'):
        try:
            max_order = len(ctype.field_groups) - 1
            if action == 'shift-left' and fg.order > 0:
                low = fg.order - 1
                high = fg.order
                for group in ctype.field_groups:
                    if group.order == low:
                        group.order = high
                    elif group.order == high:
                        group.order = low
            elif action == 'shift-right' and fg.order < max_order:
                low = fg.order
                high = fg.order + 1
                for group in ctype.field_groups:
                    if group.order == low:
                        group.order = high
                    elif group.order == high:
                        group.order = low
            db.session.commit()
            field_groups = []
            for group in ctype.field_groups:
                field_groups.append({
                    'uuid': group.uuid,
                    'name': group.name,
                    'order': group.order
                })
            return {'success': True,
                    'field_groups': field_groups}
        except:
            return {'success': False,
                    'error': ['Server error']}
    elif action == 'create-field':
        '''
        ping to pre-make a field for the field group. returns a uuid, order, 
        and default name
        '''
        try:
            
            field_names = []
            for group in ctype.field_groups:
                field_names += [f.name for f in group.fields]

            # default to first field type
            field = ContentField()
            field.type_key = field.field_types.keys()[0]
            field.order = len(fg.fields)
            field.content_type_uuid = ctype.uuid
            field.field_group_uuid = fg.uuid
            fg.fields.append(field)

            # auto generate a name
            field_i = 0
            field_name = None
            while field_name is None:
                name_try = 'field_{i}'.format(i=field_i)
                if name_try not in field_names:
                    field_name = name_try
                field_i += 1
            field.name = field_name

            db.session.add(field)
            db.session.commit()

            return {'success': True,
                    'uuid': field.uuid,
                    'name': field.name,
                    'order': field.order}
        except Exception as e:
            return {'success': False,
                    'error': [
                        'Server error',
                        'Exception message: {e}'.format(e=e)
                    ]}


@bp.route('/field/<f_uuid>/', methods=['POST'])
@api
@uuid_check
def content_type_field_edit(uuid, ctype, f_uuid):
    try:
        field = db.session.query(ContentField).\
            filter(ContentField.uuid==f_uuid, 
                   ContentField.content_type_uuid==uuid).\
            one()
    except NoResultFound as e:
        return {'success': False,
                'notice': ['Specified field not found.']}
    action = request.form.get('action')
    if action is None:
        return {'success': False,
                'notice': ['Action not specified.']}
    elif action == 'update':
        try:
            notices = []
            name = request.form.get('name', '')
            type_key = request.form.get('type_key', '')
            if len(name) < 4 or len(name) > 100:
                notices.append('Field name must be between 4 and 100 characters.')
            if name.startswith('content_entry_'):
                notices.append('Field name must not start with "content_entry_".')
            if type_key not in field.field_types.keys():
                notices.append('Field type specified is not valid.')

            if notices:
                return {'success': False,
                        'notice': notices}
            else:
                field.name = name
                field.type_key = type_key
                db.session.commit()
                return {'success': True,
                        'uuid': field.uuid,
                        'name': field.name,
                        'order': field.order,
                        'type_key': field.type_key}

        except:
            return {'success': False,
                    'error': ['Server error']}
    elif action == 'delete':
        db.session.delete(field)
        group = db.session.query(ContentFieldGroup).\
            filter(ContentFieldGroup.uuid==field.content_field_group_uuid).\
            one()
        group.fields.remove(field)
        for i, f in enumerate(group.fields):
            f.order = i
        db.session.commit()
        return {'success': True}
    elif action.startswith('shift-'):
        group = db.session.query(ContentFieldGroup).\
            filter(ContentFieldGroup.uuid==field.content_field_group_uuid).\
            one()
        max_order = len(group.fields) - 1
        fields = []
        if action == 'shift-up' and field.order > 0:
            low = field.order - 1
            high = field.order
            for f in group.fields:
                if f.order == low:
                    f.order = high
                elif f.order == high:
                    f.order = low
        elif action == 'shift-down' and field.order < max_order:
            low = field.order
            high = field.order + 1
            for f in group.fields:
                if f.order == low:
                    f.order = high
                elif f.order == high:
                    f.order = low
        db.session.commit()
        for f in group.fields:
            fields.append({
                'uuid': f.uuid,
                'name': f.name,
                'order': f.order
            })
        return {'success': True,
                'fields': fields}

@bp.route('/entry/<any(add, edit):action>/')
def entry_type_list(action):
    ctypes = g.account.content_types
    if action == 'add':
        title = 'Select the content type entry to create'
    elif action == 'edit':
        title = 'Select the content type to browse'
    template = 'manager/cms/entry-add-edit-list.jade'
    return render_template(
        template, 
        title=title, 
        ctypes=ctypes, 
        action=action)
    

@bp.route('/entry/add/<uuid>/', methods=['GET', 'POST'])
@uuid_check
def entry_add(uuid, ctype):
    form = ctype.entry_form(request.form)
    setattr(form, '_action', 'add')
    entry = None
    if request.method == 'POST' and form.validate():
        try:
            entry = ContentEntry()
            entry.content_type_uuid = uuid
            entry.title = request.form.get('content_entry_title')
            entry.slug = request.form.get('content_entry_slug')
            entry.tag = request.form.getlist('content_entry_tag')
            entry.content_type_status_uuid = request.form.get('content_entry_status')
            entry.account_id = g.account.id

            revision = ContentRevision()
            revision.account_user_id = g.user.id
            revision.field_data = {k: v for k, v in form.data.iteritems() \
                                   if not k.startswith('content_entry_')}
            entry.revision = revision
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('cms.entry_edit', 
                                    uuid=uuid,
                                    euuid=entry.uuid))
        except:
            db.session.rollback()
            flash('Slug is already in use.', 'notice')

    return render_template(
        'manager/cms/entry-create.jade', 
        title='Add new {type_name} entry'.format(type_name=ctype.name),
        form=form,
        entry=entry,
        ctype=ctype)


@bp.route('/entry/edit/<uuid>/')
@bp.route('/entry/edit/<uuid>/page:<int:page>/limit:<int:limit>/')
@uuid_check
def entry_list(uuid, ctype, page=0, limit=10):
    entries = cms.entries(ctype, page, limit, status='*')
    if entries['page_prev']:
        entries['url_prev'] = url_for(
            'cms.entry_list', 
            uuid=uuid,
            page=page-1,
            limit=limit)

    if entries['page_next']:
        entries['url_next'] = url_for(
            'cms.entry_list', 
            uuid=uuid,
            page=page+1,
            limit=limit)

    return render_template(
        'manager/cms/entry-list.jade',
        title='Edit {type_name} entry'.format(type_name=ctype.name),
        cms_entries=cms.entries,
        entries=entries,
        ctype=ctype)


@bp.route('/entry/edit/<uuid>/<euuid>/', methods=['GET', 'POST'])
@uuid_check
def entry_edit(uuid, ctype, euuid):
    try:
        entry = db.session.query(ContentEntry).\
            filter(ContentEntry.uuid==euuid).\
            one()
    except:
        return redirect(url_for('cms.entry_add', uuid=uuid))

    form = ctype.entry_form(request.form, **entry.form_data)
    setattr(form, '_action', 'edit')
    if request.method == 'POST':
        if request.form.get('content_entry_save') == 'Save' and \
           form.validate():
            try:
                entry.title = request.form.get('content_entry_title')
                entry.slug = request.form.get('content_entry_slug')
                entry.tag = request.form.getlist('content_entry_tag')
                entry.content_type_status_uuid = request.form.get('content_entry_status')

                revision = ContentRevision()
                revision.account_user_id = g.user.id
                revision.field_data = {k: v for k, v in form.data.iteritems() \
                                       if not k.startswith('content_entry_')}
                entry.revision = revision
                db.session.add(entry)
                db.session.commit()
            except:
                db.session.rollback()
                flash('Slug is already in use.', 'notice')
        elif request.form.get('content_entry_delete') == 'Delete':
            try:
                db.session.delete(entry)
                db.session.commit()
                return redirect(url_for('cms.entry_list', uuid=uuid))
            except:
                db.session.rollback()
                flash('Server error trying to delete the entry. Please try again later.', 'notice')
    return render_template(
        'manager/cms/entry-edit.jade', 
        title='Edit {type_name} entry'.format(type_name=ctype.name),
        form=form,
        entry=entry,
        ctype=ctype)

