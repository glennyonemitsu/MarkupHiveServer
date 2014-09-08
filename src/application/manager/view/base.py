from flask import g, flash, render_template, session, url_for, request, redirect

from application.blueprint import manager as bp
import service
from service import mailer
from server_global import config, db, rds


@bp.route('/')
def home():
    return render_template('manager/home.jade', title='Dashboard')


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = None
        for u in g.account.users:
            if user is None and u.username == request.form['username']:
                user = u
        if user is not None:
            if user.valid_password(request.form['password']):
                session['logged in'] = True
                session['account id'] = g.account.id
                session['user id'] = user.id
                return redirect(url_for('.home'))
            else:
                flash('Login incorrect', 'notice')
        else:
            service.feign_hash(13)
            flash('Login incorrect', 'notice')
    return render_template(
        'manager/login.jade', 
        first_registration=request.args.get('first_registration')
    )


@bp.route('/logout/')
def logout():
    session.pop('logged in', None)
    session.pop('account id', None)
    session.pop('user id', None)
    return redirect(url_for('.login'))


@bp.route('/forgot-password/', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        found = False
        for user in g.account.users:
            if not found:
                if user.username == request.form.get('username') or \
                   user.email == request.form.get('email'):
                    found = True
                    email = user.email
                    user_id = user.id
                    token = service.uuid()

                    try:
                        # save token to redis
                        key = 'password-reset:{token}'.format(token=token)
                        expires = 86400
                        rds.setex(key, expires, user_id)

                        # send reset email
                        username = user.username
                        url = url_for('manager.password_reset', token=token)
                        full_url = '{app}.{suffix}{path}'.format(
                            app=g.account.name, 
                            suffix=config.DOMAIN_SUFFIX_MANAGER,
                            path=url)
                        mailer.password_reset(username, full_url, email)
                    except:
                        notice = 'There was a problem. Please try again later.'
                        found = None

        if found is not None:
            if found:
                notice = 'Reset link sent to email address {email}'.format(email=email)
            else:
                notice = 'No user with that username or email found for this account'
        flash(notice, 'notice')
    return render_template(
        'manager/forgot-password.jade')


@bp.route('/password-reset/<token>/', methods=['GET', 'POST'])
def password_reset(token):
    key = 'password-reset:{token}'.format(token=token)
    user_id = rds.get(key)

    # check if the uuid token in the app account is valid
    valid = False
    target_user = None
    if user_id:
        user_id = int(user_id)
        for user in g.account.users:
            if not valid and user.id == user_id:
                target_user = user
                valid = True

    # token seems bad. let's end it here with a warning
    if not valid:
        return render_template('manager/password-reset-bad-token.jade')

    # everything is ok, go ahead
    if request.method == 'POST':
        password = request.form.get('password', '')
        if len(password) < 6:
            flash('Password must be at least six (6) characters.', 'notice')
        else:
            target_user.password = service.make_hash(password)
            db.session.add(target_user)
            db.session.commit()
            rds.delete(key)
            flash(
                'Password has been updated for user {0}.'.format(target_user.username), 
                'notice')
            return redirect(url_for('manager.login'))

    return render_template('manager/password-reset.jade')


