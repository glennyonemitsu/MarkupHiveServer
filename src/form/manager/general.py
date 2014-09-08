'''
General individual forms used around the manager back end
'''
from wtforms import TextField
from wtforms.validators import Length, URL, ValidationError

from form.manager import Form


class CanonicalDomainForm(Form):

    canonical_domain = TextField('Domain', [Length(max=250)])

    def validate_canonical_domain(form, field):
        domain = field.data
        if '.' not in domain or \
           '..' in domain or \
           domain.startswith('.') or \
           domain.endswith('.'):
            raise ValidationError('Domain provided is not in correct format.')

