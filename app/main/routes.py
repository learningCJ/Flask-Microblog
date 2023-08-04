from app.main import bp
from app.main.forms import AboutSiteForm, EditProfileForm
from app.models import TechStack, User, Post, Comment, Article
from app import db
from flask import render_template, flash,redirect, url_for,current_app, request, session, jsonify
from flask_login import current_user, login_required
import sqlalchemy as sa
from flask_babel import _
from app.main.forms import EmptyForm
from app.blog.routes import get_articles_with_tags_series
from app.shared_functions import anonymous_avatar


@bp.before_request
def before_request():
    current_app.jinja_env.globals.update(anonymous_avatar=anonymous_avatar)
    
@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
def index():
    return redirect(url_for('blog.index'))

@bp.route('/about', methods=['GET','POST'])
def about():
    form = AboutSiteForm()
    if form.validate_on_submit():
        techStack = TechStack(techType=form.techType.data, techName=form.techName.data, category = form.category.data)
        db.session.add(techStack)
        db.session.commit()
        flash(_('Changes made successfully!'))
        return redirect(url_for('main.about'))
    techs = db.session.scalars(sa.select(TechStack))
    admin = current_user.is_authenticated and current_user.email == current_app.config['ADMIN']
    return render_template('about.html', title=_('About'), form=form, techs=list(techs), admin=admin)

@bp.route('/resume', methods=['GET'])
def resume():
    return render_template('ChrisJeong.html', title=_('Resume'))

@bp.route('/deleteTech/<techID>', methods=["POST"])
@login_required
def deleteTech(techID):
    form = EmptyForm()
    if form.validate_on_submit():
        tech = db.session.get(TechStack, techID)
        if tech is None:
            flash(_('The tech you deleted could not be found'))
            return redirect(request.referrer)
        tech.delete()
        db.session.commit()
        flash(_('You have successfully deleted the tech!'))
        return redirect(request.referrer)
    else:
        return redirect(url_for('microblog.about'))
    
@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.session.scalar(sa.select(User).filter_by(username=username))
    if user is None:
        flash(_('User %(username)s not found', username=username))
        return redirect(url_for('microblog.index'))
    page = request.args.get('page', default=1, type=int)
    posts = db.paginate(sa.select(Post).where(Post.author==user).order_by(Post.timestamp.desc()), 
                                  page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url=url_for('main.user', username=username, page=posts.next_num) \
        if posts.has_next else None
    prev_url=url_for('main.user', username=username, page=posts.prev_num) \
        if posts.has_prev else None
    form=EmptyForm()
    return render_template('user.html', title = _('Profile'), user=user, posts = posts.items, 
                           form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    form = EditProfileForm(original_username =current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been made!'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_("Edit Profile"),  form = form)

@bp.route('/admin', methods=['GET','POST'])
def admin():
    if current_user.is_anonymous or not current_user.isAdmin():
        flash(_('Insufficient Prvilege'))
        return redirect(url_for('blog.index'))
    pendingComments = db.session.scalars(Comment.fetch_pending_approval_comments()).all()
    draftArticles = db.session.scalars(Article.fetch_draft().order_by(Article.timestamp.desc())).all()
    emptyForm = EmptyForm()
    articles_with_tags, series_with_articles = get_articles_with_tags_series()
    return render_template('admin.html', title=_('Admin'), emptyForm=emptyForm, articles_with_tags=articles_with_tags, 
                           series_with_articles=series_with_articles, 
                           pendingComments=pendingComments, draftArticles=draftArticles)

@bp.route('/approve/<c_id>', methods=['POST'])
def approve(c_id):
    form = EmptyForm()
    if form.validate_on_submit():
        comment = db.session.get(Comment,c_id)
        if not comment:
            flash('Comment does not exist')
            return redirect(url_for('main.admin'))
        comment.approve()
        db.session.commit()
        flash('Comment has been approved')
        return redirect(url_for('main.admin'))
    
@bp.route('/deny/<c_id>', methods=['POST'])
def deny(c_id):
    form = EmptyForm()
    if form.validate_on_submit():
        comment = db.session.get(Comment,c_id)
        if not comment:
            flash('Comment does not exist')
            return redirect(url_for('main.admin'))
        comment.deny()
        db.session.commit()
        flash('Comment has been deleted')
        return redirect(url_for('main.admin'))
    
@bp.route('/toggle-dark-mode', methods=['POST'])
def enable_dark_mode():
    session['dark_mode'] = not session['dark_mode']
    return jsonify({'dark-mode': session['dark_mode'], 'status':'success'})

@bp.route('/get-session-data', methods=['GET'])
def get_session_darkmode():
    dark_mode = session.get('dark-mode', False)
    return jsonify({'dark-mode': dark_mode})
