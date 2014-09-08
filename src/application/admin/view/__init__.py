from flask import (
    abort, current_app, g, redirect, render_template, request, session, 
    url_for
)

from application.blueprint import admin as bp
from model import Admin
from server_global import db
import service

from application.admin.view import account, general, plan, stripe



@bp.before_request
def admin_check():
    unchecked_endpoints = ('admin.login', 'admin.logout')
    if 'admin username' not in session and \
       request.endpoint not in unchecked_endpoints:
        abort(404)


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            query = db.session.query(Admin).\
                filter(Admin.username==request.form.get('username'))
            user = query.one()
            if user.valid_password(request.form.get('password')):
                session['admin username'] = user.username
                return redirect(url_for('admin.home'))
        except Exception as e:
            # stop timing clues
            service.feign_hash(15)
    return render_template('admin/login.jade')


@bp.route('/logout/')
def logout():
    if 'admin username' in session:
        del session['admin username']
    return redirect(url_for('admin.login'))


