from app.blog import bp
from app.blog.forms import BlogPostForm, CommentForm
from app.main.forms import EmptyForm
from app.shared_functions import text_linkification, anonymous_avatar
from app import db
from flask_login import current_user
from flask import flash, redirect, url_for, render_template, request, current_app, g
from flask_babel import _
from app.models import Article, Tag, Comment
import sqlalchemy as sa
from datetime import datetime

@bp.before_request
def before_request():
    tags={}
    page = request.args.get('page', default=1, type=int)
    articles = db.paginate(Article.fetch_submitted().order_by(Article.timestamp.desc()),
     page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    #Creating a dictionary with artcicle - list of tags to display the tags on the articles of this page
    for article in articles:
        for tag in db.session.scalars(article.tags.select()).all():
            if article not in tags:
                tags[article] = [tag.name.strip()]
            else:
                tags[article].append(tag.name.strip()) 
    g.tags = tags

    all_tags = db.session.scalars(Tag.fetch_all_tags().order_by(Tag.name)).all()
    g.all_tags = all_tags

    current_app.jinja_env.globals.update(anonymous_avatar=anonymous_avatar)

def tag_article(article, strTags):
    for tag in strTags:
        if tag:
            tag = tag.strip()
            t = db.session.scalar(sa.Select(Tag).filter_by(name=tag))
            if not t:
                t = Tag(name=tag)
                db.session.add(t)
            article.tag(t)
    

@bp.route('/add', methods=['GET','POST'])
def add():
    if current_user.is_anonymous or not current_user.isAdmin():
        flash(_('Insufficient Prvilege'))
        return redirect(url_for('blog.index'))
    form = BlogPostForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data, update_timestamp=None, author = current_user)
        if form.submit.data:
            article.isSubmitted = True
        else:
            article.isSubmitted = False
        db.session.add(article)
        db.session.commit()
        tag_article(article,form.tags.data.split(','))
        db.session.commit()
        if form.submit.data:
            flash(_('Article has been submitted!'))
            return redirect(url_for('blog.article', id=article.id))
        else:
            flash(_('Article has been saved to drafts!'))
            return redirect(url_for('blog.edit', id=article.id))

    return render_template('blog/add_edit_blog.html', title = _('Add Blog Post'), form=form)

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
def index():
    emptyForm = EmptyForm()
    page = request.args.get('page', default=1, type=int)
    articles = db.paginate(Article.fetch_submitted().order_by(Article.timestamp.desc()),
     page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url=url_for('blog.index', page=articles.next_num) \
        if articles.has_next else None
    prev_url=url_for('blog.index', page=articles.prev_num) \
        if articles.has_prev else None
    
    return render_template('blog/blog.html', title=_('Blog'), articles = articles, next_url=next_url, prev_url=prev_url, emptyForm=emptyForm)

@bp.route('/article/<id>', methods=['GET','POST'])
def article(id):
    emptyForm = EmptyForm()
    commentForm = CommentForm()
    article = db.session.scalar(Article.fetch_article(id))
    if article is None:
        flash(_('The article you deleted could not be found'))
        return redirect(request.referrer)
    comments = db.session.scalars(article.fetch_approved_comments()).all()
    #Clear validators for username and email for loggedin users
    if current_user.is_authenticated:
        commentForm.username.validators = []
        commentForm.email.validators = []
    if commentForm.validate_on_submit():
        commentForm.comment.data = text_linkification(commentForm.comment.data)
        if current_user.is_authenticated:
            comment = Comment(comment=commentForm.comment.data, article=article, commenter=current_user, isApproved=True)
        else:
            comment = Comment(comment=commentForm.comment.data, article=article, 
                              name=commentForm.username.data, email=commentForm.email.data, isApproved=False)
        db.session.add(comment)
        db.session.commit()
        
        if current_user.is_anonymous:
            flash(_('Comment submitted for review. Your comment will be visible once approved'))
        else:
            flash(_('Comment added successfully'))

        return redirect(url_for('blog.article', id = id))

    return render_template('blog/article.html', title=_(article.title), article=article, commentForm=commentForm, 
                           emptyForm = emptyForm,  comments=comments)

@bp.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if current_user.is_anonymous or not current_user.isAdmin():
        flash(_('Insufficient Prvilege'))
        return redirect(url_for('blog.index'))
    article = db.session.get(Article,id)
    if not article:
        flash('The article could not be found')
        return redirect(url_for('blog.index'))
    if current_user != article.author:
        flash('Only the original author can update the article')
        return redirect(url_for('blog.index'))
    form = BlogPostForm()
    stringTags = ""

    if form.validate_on_submit():
        article.title = form.title.data
        article.body = form.body.data
        article.update_timestamp = datetime.utcnow()
        articleTagList = db.session.scalars(article.tags.select()).all()
        if form.submit.data:
            article.isSubmitted = True
        else:
            article.isSubmitted = False
        for tag in articleTagList:
            article.untag(tag)

        #Let's put below in a method somewhere. It's shared with adding
        tag_article(article,form.tags.data.split(','))
        db.session.commit()
        if form.submit.data:
            flash(_('Article has been Edited!'))
            return redirect(url_for('blog.article', id=article.id))
        else:
            flash(_('Article has been saved to drafts!'))
            return redirect(url_for('blog.edit', id=article.id))
        
    elif request.method =='GET':
        form.title.data=article.title
        form.body.data=article.body
        articleTagList = db.session.scalars(article.tags.select()).all()
        for tag in articleTagList:
            if stringTags == "":
                stringTags = tag.name
            else:
                stringTags += ", "+ tag.name
        form.tags.data = stringTags

    return render_template('blog/add_edit_blog.html', title = _('Edit Blog Post'), form=form)


@bp.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    form = EmptyForm()
    if form.validate_on_submit():
        article = db.session.get(Article,id)
        if article is None:
            flash(_('The article you deleted could not be found'))
            return redirect(url_for('blog.index'))
        article.delete()
        db.session.commit()
        flash(_('You have successfully deleted the article!'))
        return redirect(url_for('blog.index'))

@bp.route('/delete-comment/<c_id>', methods=['POST'])
def delete_comment(c_id):
    form = EmptyForm()
    if form.validate_on_submit():
        comment = db.session.get(Comment, c_id)
        if comment is None:
            flash(_('The comment you deleted could not be found'))
            return redirect(request.referrer)
        comment.delete()
        db.session.commit()
        flash(_('You have successfully deleted the comment!'))
        return redirect(request.referrer)

@bp.route('/tag/<tag>', methods=['GET'])
def tag(tag):
    tag = db.session.scalar(sa.select(Tag).filter_by(name=tag))
    emptyForm = EmptyForm()
    page = request.args.get('page', default=1, type=int)
    articles = db.paginate(tag.tagged_submiited_articles_select().order_by(Article.timestamp.desc()),
     page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url=url_for('blog.tag', tag=tag, page=articles.next_num) \
        if articles.has_next else None
    prev_url=url_for('blog.tag', tag=tag, page=articles.prev_num) \
        if articles.has_prev else None
    all_tags = db.session.scalars(sa.select(Tag))
    return render_template('blog/blog.html', title=_('Blog'), articles = articles, emptyForm = emptyForm, next_url=next_url, prev_url=prev_url, all_tags=all_tags,tags=g.get('tags',{}))


