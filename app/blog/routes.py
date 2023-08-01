from app.blog import bp
from app.blog.forms import BlogPostForm, CommentForm
from app.main.forms import EmptyForm
from app.shared_functions import text_linkification, anonymous_avatar
from app import db, cache
from flask_login import current_user
from flask import flash, redirect, url_for, render_template, request, current_app, g
from flask_babel import _
from app.models import Article, Tag, Comment
import sqlalchemy as sa
from datetime import datetime

@bp.before_request
def before_request():
    g.all_tags = get_all_tags()

def tag_article(article, strTags):
    for tag in strTags:
        if tag:
            tag = tag.strip()
            t = db.session.scalar(sa.Select(Tag).filter_by(name=tag))
            if not t:
                t = Tag(name=tag)
                db.session.add(t)
            article.tag(t)

def get_all_tags():
    all_tags = cache.get('all_tags')

    if all_tags:
        return all_tags

    all_tags = db.session.scalars(Tag.fetch_all_tags().order_by(Tag.name)).all()
    return all_tags

def get_articles_with_tags_series():
    articles_with_tags = cache.get('articles_with_tags')
    series_with_articles = cache.get('series_with_articles')

    if articles_with_tags and series_with_articles:
        return articles_with_tags, series_with_articles 

    articles = db.session.scalars(Article.fetch_submitted()).all()
    
    articles_with_tags={}
    series_with_articles = {}

    for article in articles:
        for tag in db.session.scalars(article.tags.select()).all():
            if article.id not in articles_with_tags:
                articles_with_tags[article.id] = [tag.name.strip()]
            else:
                articles_with_tags[article.id].append(tag.name.strip())
        if article.series and article.series not in series_with_articles:
            series_with_articles[article.series] = list(db.session.scalars(Article.fetch_all_series(article.series).order_by(
                Article.seriesOrder)).all()) 

    cache.set('articles_with_tags', articles_with_tags, timeout=3600)
    cache.set('series_with_articles', series_with_articles, timeout=3600)
    return articles_with_tags, series_with_articles

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
    
    articles_with_tags, series_with_articles = get_articles_with_tags_series()
    
    return render_template('blog/blog.html', title=_('Blog'), articles = articles, articles_with_tags=articles_with_tags,
                           series_with_articles=series_with_articles, next_url=next_url, prev_url=prev_url, emptyForm=emptyForm)

@bp.route('/add', methods=['GET','POST'])
def add():
    if current_user.is_anonymous or not current_user.isAdmin():
        flash(_('Insufficient Prvilege'))
        return redirect(url_for('blog.index'))
    form = BlogPostForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data, body=form.body.data, update_timestamp=None, 
                          author = current_user, series = form.series.data, seriesOrder = form.seriesOrder.data)
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
    cache.clear()
    return render_template('blog/add_edit_blog.html', title = _('Add Blog Post'), form=form)



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

        redirect_url = url_for('blog.article', id = id )+"#articleComments"
        return redirect(redirect_url)

    articles_with_tags, series_with_articles = get_articles_with_tags_series()

    return render_template('blog/article.html', title=_(article.title), article=article, commentForm=commentForm, 
                           articles_with_tags=articles_with_tags, series_with_articles=series_with_articles, emptyForm = emptyForm,  comments=comments)

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
        article.series = form.series.data
        article.seriesOrder = form.seriesOrder.data
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
        form.series.data=article.series
        form.seriesOrder.data=article.seriesOrder
        articleTagList = db.session.scalars(article.tags.select()).all()
        for tag in articleTagList:
            if stringTags == "":
                stringTags = tag.name
            else:
                stringTags += ", "+ tag.name
        form.tags.data = stringTags
    cache.clear()
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
        cache.clear()
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

    articles_with_tags, series_with_articles = get_articles_with_tags_series()

    return render_template('blog/blog.html', title=_('Blog'), articles = articles, articles_with_tags = articles_with_tags, series_with_articles = series_with_articles,
                           emptyForm = emptyForm, next_url=next_url, prev_url=prev_url, all_tags=all_tags,tags=g.get('tags',{}))


