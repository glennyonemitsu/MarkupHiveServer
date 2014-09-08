from flask import (
    abort, current_app, flash, g, redirect, render_template, request, 
    session, url_for
)

from application.blueprint import admin as bp
from form.admin import PlanForm
from model import Plan
from server_global import db
import service


@bp.route('/plan/')
def plan_home():
    plans = db.session.query(Plan).all()
    return render_template('admin/plan-home.jade', plans=plans)


@bp.route('/plan/create/', methods=['GET', 'POST'])
def plan_create():
    form = PlanForm(request.form)
    if request.method == 'POST' and form.validate():
        plan = Plan()
        form.populate_obj(plan)
        db.session.add(plan)
        db.session.commit()
        return redirect(url_for('.plan_home'))
    return render_template('admin/plan-create.jade', form=form)


@bp.route('/plan/<int:plan_id>/', methods=['GET', 'POST'])
def plan_edit(plan_id):
    try:
        plan = db.session.query(Plan).\
            filter(Plan.id==plan_id).one()
        form = PlanForm(request.form, plan)
        if request.method == 'POST' and form.validate():
            form.populate_obj(plan)
            db.session.add(plan)
            db.session.commit()
            return redirect(url_for('.plan_home'))
        return render_template('admin/plan-edit.jade', form=form)
    except Exception as e:
        return redirect(url_for('.plan_home'))
