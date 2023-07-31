from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from app import db
import sqlalchemy as sa
from app.models import User
from flask_babel import lazy_gettext as _l, _
from flask import request

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say Something!'), validators=[Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

    def validate_post(self, post):
        if not post.data.strip():
            raise ValidationError(_('Post cannot be blank!'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    password = PasswordField(_l('Enter New Password'), validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField(_l('Please Confirm your New Password'), validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(_l('Reset Password'))

    def validate_password(self, password):
        if password.data.find(self.user.username)>=0:
            raise ValidationError(_('Password is not allowed to contain your username.'))
        
        if self.user.check_password(password.data):
            raise ValidationError(_('Your new password cannot be the same as the current one.'))
        
class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf':False}
        super(SearchForm, self).__init__(*args, **kwargs)

