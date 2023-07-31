from app import db
from flask import render_template, flash,redirect, url_for, request, g, jsonify, current_app
from flask_login import login_required, current_user
from app.main.forms import EmptyForm
import sqlalchemy as sa
from app.models import User, Post, TechStack
from app.shared_functions import text_linkification
from datetime import datetime
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from app.translate import translate
from app.microblog import bp
from app.microblog.forms import SearchForm, PostForm
import re

@bp.before_request
def before_request():
    if current_user.is_authenticated: 
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
    persistentMsg = ''
    form = PostForm()
    if form.validate_on_submit():
        if not current_user.isVerified:
            flash(_('Please confirm your email from Profile'))
            return redirect(url_for('microblog.index'))
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language =''
        form.post.data = text_linkification(form.post.data)
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('microblog.index'))
    page = request.args.get('page', default=1, type=int)
    posts = db.paginate(current_user.followed_posts_select().order_by(Post.timestamp.desc()), 
                        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url=url_for('microblog.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url=url_for('microblog.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('microblog/index.html', title=_('Home'),  posts = posts, form = form, next_url=next_url, prev_url=prev_url)



@bp.route('/follow/<username>', methods=['Post'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).filter_by(username=username))
        if user is None:
            flash(_('User %(username)s not found', username=username))
            return redirect(url_for('microblog.index'))
        if current_user == user:
            flash(_('You cannot follow yourself'))
            return redirect(url_for('microblog.user', username=user.username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You have successfully followed %(username)s', username=username))
        return redirect(request.referrer)
    else:
        return redirect(url_for('microblog.index'))
    
@bp.route('/unfollow/<username>', methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).filter_by(username=username))
        if user is None:
            flash('User {} could not be found'.format(username))
            return redirect(url_for('microblog.index'))
        if current_user == user:
            flash(_('You cannot unfollow yourself'))
            return redirect(url_for('microblog.index'))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You have unfollowed %(username)s successfully', username=username))
        return redirect(request.referrer)
    else:
        return redirect(url_for('microblog.index'))
    

@bp.route('/explore')
def explore():
    form = EmptyForm()
    page = request.args.get('page', default=1, type=int)
    posts = db.paginate(sa.select(Post).order_by(Post.timestamp.desc()),
                        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('microblog.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('microblog.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('microblog/index.html', title=_("Explore"), posts = posts.items, next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/delete/<postID>', methods=["POST"])
@login_required
def delete(postID):
    form = EmptyForm()
    if form.validate_on_submit():
        post = db.session.get(Post, postID)
        if post is None:
            flash(_('The post you deleted could not be found'))
            return redirect(request.referrer)
        post.delete()
        db.session.commit()
        flash(_('You have successfully deleted the post!'))
        return redirect(request.referrer)
    else:
        return redirect(url_for('microblog.index'))
    
@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})    

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('microblog.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('microblog.search', q=g.search_form.q.data, page=page+1) if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('microblog.search', q=g.search_form.q.data, page=page-1) if page > 1 else None
    form = EmptyForm()
    return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url, form=form)

