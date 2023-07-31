from flask import Blueprint

bp = Blueprint('microblog', __name__)

from app.microblog import routes