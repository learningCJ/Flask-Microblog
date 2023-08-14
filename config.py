import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir,'.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ZcO6rLTyebOXXEPOHihDoX7G'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.sendgrid.net"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "apikey"

    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_SUPPORT_SENDER = os.environ.get('MAIL_SUPPORT_SENDER')

    POSTS_PER_PAGE=10

    LANGUAGES=["en", "ko"]

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    ELASTICSEARCH_USERNAME = os.environ.get('ELASTICSEARCH_USERNAME')
    ELASTICSEARCH_PW = os.environ.get('ELASTICSEARCH_PW')
    ELASTICSEARCH_CERT_DIR = os.environ.get('ELASTICSEARCH_CERT_DIR')
    MIN_PW_LEN = 8

    #CKEDITOR
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 700
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_CODE_THEME = 'tomorrow'
    CKEDITOR_CONTENT_CSS = 'static/styles/mystle.css'
    #CKEDITOR_FILE_UPLOADER = 'upload'

    CACHE_TYPE = 'flask_caching.backends.SimpleCache'

    SESSION_COOKIE_SECURE = True  # Use HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # Prevent client-side JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # Set SameSite attribute for CSRF protection
    SESSION_DEFAULTS = {
        'dark_mode': True
    }