from app.blog import bp
from app.blog.forms import BlogPostForm, CommentForm
from app import db
from flask_login import current_user
from flask import flash, redirect, url_for, render_template, request, current_app, g
from flask_babel import _
from app.models import Article, Tag, User, Comment
import sqlalchemy as sa

@bp.route('/add', methods=['GET','POST'])
def add():
    if not current_user.isAdmin():
        flash(_('Insufficient Prvilege'))
        return redirect(url_for('blog.display_blog'))
    form = BlogPostForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data, update_timestamp=None, author = current_user, isSubmitted=True)
        db.session.add(article)
        db.session.commit()
        for tag in form.tags.data.split(','):
            if tag:
                t = db.session.scalar(sa.Select(Tag).filter_by(name=tag.strip()))
                if not t:
                    t = Tag(name=tag)
                    db.session.add(t)
                article.tag(t)
        db.session.commit()
        flash(_('Article has been submitted!'))
        return redirect(url_for('blog.index'))

    return render_template('blog/add_edit_blog.html', title = _('Add Blog Post'), form=form)

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
def index():
    page = request.args.get('page', default=1, type=int)

    all_articles = Article.fetch_submitted()
    articles = db.paginate(all_articles.order_by(Article.timestamp.desc()),
     page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    tags={}
    #Creating a dictionary with artcicle - list of tags to display the tags on the articles
    for article in db.session.scalars(all_articles).all():
        for tag in db.session.scalars(article.tags.select()).all():
            if article not in tags:
                tags[article] = [tag]
            else:
                tags[article].append(tag) 
    next_url=url_for('blog.display_blog', page=articles.next_num) \
        if articles.has_next else None
    prev_url=url_for('blog.display_blog', page=articles.prev_num) \
        if articles.has_prev else None
    
    g.tags = tags

    return render_template('blog/blog.html', title=_('Blog'), articles = articles, tags = g.tags, next_url=next_url, prev_url=prev_url)
@bp.route('/article/<id>', methods=['GET','POST'])
def article(id):
    form = CommentForm()
    article = db.session.scalar(Article.fetch_article(id))
    comments = db.session.scalars(article.fetch_approved_comments()).all()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            user = db.session.scalar(sa.select(User).filter(User.email==form.email.data))
            if user and not user.isTempAccount:
                flash('You already have an account. Please change your email or log in before submitting the comment')
                return redirect(url_for('blog.article', id = id))
            if not user:
                user = User(username=form.username.data, email=form.email.data, isVerified=False, isTempAccount=True)
                db.session.add(user)
                db.session.commit()
            comment = Comment(comment=form.comment.data, article=article, commenter=user, isApproved=False)
        else:
            comment = Comment(comment=form.comment.data, article=article, commenter=current_user, isApproved=True)
        db.session.add(comment)
        db.session.commit()
        
        if not current_user.is_authenticated:
            flash(_('Comment submitted for review. Your comment will be visible once approved'))
        else:
            flash(_('Comment added successfully'))

        return redirect(url_for('blog.article', id = id))

    return render_template('blog/article.html', title=_(article.title), article=article, tags=g.get('tags',{}), form=form, comments=comments)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    return

@bp.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    return