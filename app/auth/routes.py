from flask import render_template, flash,redirect, url_for, request
from flask_login import login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm,  ResetPasswordForm, ResetPasswordRequestForm
from flask_login import current_user, login_user, logout_user
import sqlalchemy as sa
from app.models import User
from werkzeug.urls import url_parse
from app.auth.email import send_password_confirm_reset_email
from flask_babel import _

@bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).filter_by(email = form.email.data))
        if not user or not user.check_password(form.password.data):
            flash(_('Incorrect username and/or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != "":
            return redirect(url_for('main.index'))
        return redirect(next_page)
    return render_template('auth/login.html', title = _("Sign In"), form = form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect (url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data, isVerified = False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('You have been registered and we have sent you a confirmation email'))
        send_password_confirm_reset_email(user, 'register')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_("Register"), form = form)

@bp.route('/reset_password_request', methods = ['GET', 'Post'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).filter_by(email=form.email.data))
        if user is not None and user.isVerified:
            send_password_confirm_reset_email(user, 'reset')
        flash(_('Please check your email for instructions on how to reset the password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)

@bp.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = User.verify_token(token)
    if user is None:
        flash(_('The URL was invalid. If this is an error, please contact the administrator'))
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm(user)
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been successfully updated'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@bp.route('/confirm_registration_request', methods=['GET', 'POST'])
@login_required
def confirm_registration_request():
    send_password_confirm_reset_email(current_user, 'register')
    flash(_('Confirmation email has been sent. Please check your email'))
    print(current_user.username)
    return redirect(url_for('main.user', username=current_user.username))

@bp.route('/confirm_registration/<token>', methods = ['GET', 'POST'])
def confirm_registration(token):
    user = User.verify_token(token)
    if user is None:
        flash(_('The URL was invalid. If this is an error, please contact the administrator'))
        return redirect(url_for('auth.login'))
    user.verify()
    db.session.commit()
    flash(_('Your registration is confirmed'))
    return redirect(url_for('main.index'))










