from flask import flash
from flask.ext.wtf import Form as WForm


class Form(WForm):
    '''
    Captures Validation Errors and uses manager flash setup
    '''

    def validate(self):
        super(WForm, self).validate()
        if self.errors:
            for field in self.errors:
                for error in self[field].errors:
                    flash(error, 'notice')
            return False
        else:
            return True
