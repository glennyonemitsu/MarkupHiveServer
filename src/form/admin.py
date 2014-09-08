'''
All forms for admin control panel. 

NOT the customers' manager
'''
from flask.ext.wtf import Form
from wtforms import BooleanField, DateTimeField, DecimalField, IntegerField, \
                    TextField
from wtforms.validators import InputRequired as Required

class AccountForm(Form):
    join_timestamp = DateTimeField()

    plan_code_name = TextField('Plan Code Name')
    plan_name = TextField('Customer Facing Plan Name')
    price = DecimalField('Monthly Price', places=2)

    transfer = IntegerField('Monthly Data Transfer Limit')
    size_static = IntegerField('Max Static File Size Per File')
    size_total = IntegerField('Max Upload App Size')
    count_template = IntegerField('Max Templates')
    count_static = IntegerField('Max Static File Count')

    custom_domain = BooleanField('Allow Custom Domains') 
    cms = BooleanField('CMS Enabled')


class PlanForm(Form):

    code_name = TextField(
        'Plan Code Name', [Required()])
    name = TextField(
        'Customer Facing Plan Name', [Required()])
    price = DecimalField(
        'Monthly Price', [Required()], places=2)

    transfer = IntegerField(
        'Monthly Data Transfer Limit', [Required()])
    size_static = IntegerField(
        'Max Static File Size Per File', [Required()])
    size_total = IntegerField(
        'Max Upload App Size', [Required()])
    count_template = IntegerField(
        'Max Templates', [Required()])
    count_static = IntegerField(
        'Max Static File Count', [Required()])

    custom_domain = BooleanField('Allow Custom Domains')
    cms = BooleanField('CMS Enabled')

    available = BooleanField('Available for Registration')
