from flask import render_template, session, url_for, request, redirect, g

from application.blueprint import manager as bp
from server_global import db


@bp.route('/api-keys/')
def api_keys_home():
    api_keys = g.account.api_keys
    return render_template('manager/api-keys-home.jade', title='API Keys', api_keys=api_keys)

@bp.route('/api-keys/create/')
def api_keys_create():
    g.account.add_api_key()
    db.session.commit()
    return redirect(url_for('.api_keys_home'))

@bp.route('/api-keys/delete/<access_key>/')
def api_keys_delete(access_key):
    key = g.account.get_api_key(access_key)
    db.session.delete(key)
    db.session.commit()
    return redirect(url_for('.api_keys_home'))

