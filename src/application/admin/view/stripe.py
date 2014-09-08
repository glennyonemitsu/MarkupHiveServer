from flask import (
    abort, current_app, flash, g, redirect, render_template, request, 
    session, url_for
)

from application.blueprint import admin as bp
from form.admin import PlanForm
from model import Plan
from server_global import db, config, stripelib as stripe
import service


@bp.route('/stripe/')
def stripe_home():
    plans = stripe.Plan.all()
    return render_template(
        'admin/stripe-home.jade', 
        deployment=config.DEPLOYMENT,
        plans=plans)
