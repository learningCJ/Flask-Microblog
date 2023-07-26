from app import create_app,db,cli
from app.models import User, Post, Article, Comment, Tag, post_tags
import sqlalchemy as sa

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Article':Article, 'Comment':Comment,'Tag':Tag, 'sa':sa, 'post_tags':post_tags}

