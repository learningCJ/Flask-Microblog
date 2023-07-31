import logging
from logging.handlers import SMTPHandler,RotatingFileHandler
import os
from flask import Flask,request,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel,lazy_gettext as _l
from config import Config 
from elasticsearch import Elasticsearch
import textile
from flask_ckeditor import CKEditor
from flask_session_captcha import FlaskSessionCaptcha
from flask_sessionstore import Session

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
moment = Moment()
babel = Babel()
ckeditor = CKEditor()
#captcha = FlaskSessionCaptcha()

def textile_filter(text):
     return textile.textile(text)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.filters['textile'] = textile_filter

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']], ca_certs=app.config['ELASTICSEARCH_CERT_DIR'], \
                                      basic_auth=(app.config['ELASTICSEARCH_USERNAME'], app.config['ELASTICSEARCH_PW']))\
                                        if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    ckeditor.init_app(app)
    #app.config['SESSION_SQLALCHEMY'] = db
    #Session(app)
    #captcha.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.microblog import bp as microblog_bp
    app.register_blueprint(microblog_bp, url_prefix='/microblog')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                    secure = ()
        
        mail_handler = SMTPHandler(
            mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_DEFAULT_SENDER'], subject="Microblog Error",
            toaddrs=['web.error.monitoring@gmail.com'], 
            credentials = auth, secure = secure
        )

        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('microblog.log', maxBytes=1048000, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')
        
    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    #return 'ko'

from app import models





    
