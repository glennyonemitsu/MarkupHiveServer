from flask import make_response, render_template, session, url_for, request, redirect, g

from application.blueprint import manager as bp
from server_global import db

from form.manager.general import CanonicalDomainForm


@bp.route('/canonical-domain/', methods=['GET', 'POST'])
def canonical_domain():
    if not g.account.custom_domain:
        return make_response(render_template('manager/not-found.jade'), 404)

    domain = g.account.canonical_domain
    form = CanonicalDomainForm(request.form, g.account)

    if request.method == 'POST' and form.validate():
        form.populate_obj(g.account)
        db.session.commit()
    
    return render_template('manager/canonical-domain.jade', 
                           title='Canonical Domain',
                           form=form,
                           domain=domain)

