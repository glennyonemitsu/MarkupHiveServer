'''
All forms for customers' manager back end.
'''
from flask.ext.wtf import Form
from wtforms import BooleanField, DateTimeField, DecimalField, IntegerField, \
                    TextField, SelectField
from wtforms.validators import Length, InputRequired as Required

from form.manager.cms_field_type import field_types


class ContentTypeForm(Form):

    name = TextField('Name', [Required()])
    description = TextField('Description (optional)', [Length(max=250)])


class FieldTypeForm(Form):
    pass

    #field_type = SelectField(
    #    'Field Type', 
    #    choices=[(k, v.label) for k, v in field_types.iteritems()])

