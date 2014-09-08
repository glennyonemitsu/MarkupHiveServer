'''
Field definitions for CMS
'''
from collections import OrderedDict

from wtforms.fields import TextField, TextAreaField
from wtforms.widgets import TextArea


class RichTextArea(TextArea):
    pass


class RichTextAreaField(TextAreaField):
    pass


# attached to the flask app object to use in cms
field_types = OrderedDict()
field_types['small_text'] = {'label': 'Text Field',
                             'field': TextField}
field_types['large_text'] = {'label': 'Text Area Field',
                             'field': TextAreaField}
field_types['rte'] = {'label': 'Rich Text Editor',
                      'field': RichTextAreaField}
