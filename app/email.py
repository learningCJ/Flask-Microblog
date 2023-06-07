from flask_mail import Message
from flask import current_app
from threading import Thread
from app import mail

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, sender, body_text, body_html):
    msg = Message(subject,
                  recipients=recipients,
                  sender=sender)
    msg.body = body_text
    msg.html = body_html
    Thread(target=send_async_email, args=(current_app._get_current_object(),msg)).start()
