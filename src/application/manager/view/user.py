from flask import g, flash, render_template, session, url_for, request, redirect

from application.blueprint import manager as bp
from server_global import db
import service

@bp.route('/user/password/', methods=['GET', 'POST'])
def password_change():
    if request.method == 'POST':
        user = g.account.users[0]
        valid = True
        if not user.valid_password(request.form.get('old')):
            flash('Original password is not valid', 'notice')
            valid = False
        if request.form.get('new') != request.form.get('confirm'):
            flash('New password and confirmation does not match', 'notice')
            valid = False
        elif len(request.form.get('new')) < 6:
            flash('New password does not meet minimum length of six characters', 'notice')
            valid = False
        if valid:
            user.password = service.make_hash(request.form.get('new'))
            db.session.commit()
            flash('Password changed', 'success')

    return render_template('manager/password-change.jade', title='Reset Password')
