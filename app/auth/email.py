from flask_babel import _
from flask import render_template, current_app
from app.email import send_email

def send_password_confirm_reset_email(user, reqType):
    token = user.get_register_reset_password_token()

    if reqType.lower() == "reset":
        send_email(_('[ChrisJeong.ca]Reset Password'),
                recipients=[user.email],
                sender=current_app.config['MAIL_SUPPORT_SENDER'],
                body_text=render_template('email/reset_password.txt', user=user, token=token),
                body_html=render_template('email/reset_password.html', user=user, token=token)
                )
        
    elif reqType.lower() == "register":
        send_email(_('[ChrisJeong.ca]Confirm Registration'),
                recipients=[user.email],
                sender=current_app.config['MAIL_SUPPORT_SENDER'],
                body_text=render_template('email/confirm_registration.txt', user=user, token=token),
                body_html=render_template('email/confirm_registration.html', user=user, token=token)
                )