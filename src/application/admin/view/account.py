from flask import (
    abort, current_app, flash, g, redirect, render_template, request, 
    session, url_for
)

from application.blueprint import admin as bp
from form.admin import AccountForm
from model import Account
from server_global import db
import service


@bp.route('/account/', methods=['GET', 'POST'])
def account_home():
    accounts = []
    name = request.form.get('name')
    if request.method == 'POST' and name:
        like_name = '%{name}%'.format(name=name)
        query = db.session.query(Account).\
            filter(Account.name.like(like_name))
        accounts = query.all()
    
    return render_template('admin/account/home.jade', accounts=accounts, name=name)


@bp.route('/account/<int:account_id>/', methods=['GET', 'POST'])
def account_edit(account_id):
    try:
        account = db.session.query(Account).\
            filter(Account.id==account_id).one()
    except:
        return redirect(url_for('.account_home'))
    form = AccountForm(request.form, account)
    if request.method == 'POST' and form.validate():
        form.populate_obj(account)
        db.session.add(account)
        db.session.commit()
    return render_template('admin/account/edit.jade', account=account, form=form)


