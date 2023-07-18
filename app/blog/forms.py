from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, validators
from wtforms.validators import DataRequired, Length, Email, ValidationError, Optional
from flask_ckeditor import CKEditorField
from flask_babel import lazy_gettext as _l, _


class BlogPostForm(FlaskForm):
    title = StringField(_('Title'), validators=[DataRequired(), Length(min=1, max=100)])
    body = CKEditorField(validators=[DataRequired(), Length(min=1, max=4000)])
    tags = StringField(_('Tags:'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class CommentForm(FlaskForm):
    username = StringField(_('Name'),  validators=[Optional(), Length(min=1, max=64)])
    email = EmailField(_('Email'), validators=[validators.Optional(), Email()])
    comment = StringField(_('Comment'),  validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

   

