from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_ckeditor import CKEditorField
from flask_babel import lazy_gettext as _l, _
from app import db
import sqlalchemy as sa
from app.models import User


class BlogPostForm(FlaskForm):
    title = StringField(_('Title'), validators=[DataRequired(), Length(min=1, max=90)])
    body = CKEditorField(validators=[DataRequired(), Length(min=1, max=25000)])
    tags = StringField(_('Tags:'), validators=[DataRequired()])
    save = SubmitField(_l('Save'))
    submit = SubmitField(_l('Submit'))

class CommentForm(FlaskForm):
    username = StringField(_('Name'),  validators=[DataRequired(), Length(min=1, max=64)])
    email = EmailField(_('Email'), validators=[DataRequired(), Email()])
    comment = TextAreaField(_('Comment'),  validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
    
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).filter_by(username=username.data))
        if user is not None:
            raise ValidationError(_('Username already exists! Please choose another name'))
   

