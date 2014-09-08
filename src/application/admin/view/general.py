from flask import (
    abort, current_app, flash, g, redirect, render_template, request, 
    session, url_for
)

from application.blueprint import admin as bp
from server_global import db
import service


@bp.route('/')
def home():
    return render_template('admin/home.jade')


