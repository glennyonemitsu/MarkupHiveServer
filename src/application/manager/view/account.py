from flask import render_template, session, url_for, request, redirect, g

from application.blueprint import manager as bp


@bp.route('/account/')
def account_home():
    return render_template('manager/account-home.jade')


@bp.route('/account/add-app-domain/', methods=['POST'])
def add_app_domain():
    return redirect(url_for('.account_home'))
