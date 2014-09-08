from flask import g, redirect, url_for

from application.blueprint import cms as bp

from . import content_type


@bp.before_request
def before_request():
    if not g.account.cms:
        return redirect(url_for('manager.home'))
