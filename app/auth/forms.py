from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from app import db
import sqlalchemy as sa
from app.models import User
from flask_babel import lazy_gettext as _l
from flask_babel import _
from string import ascii_lowercase, ascii_uppercase, digits
import re

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    show_pw = BooleanField(_l('Show Password'))
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(),Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField(_l('Please Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    show_pw = BooleanField(_l('Show Password'))
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        #checks whether the username already exists
        user = db.session.scalar(sa.select(User).filter_by(username = username.data.strip()))

        if user is not None:
            raise ValidationError(_('The Username %(username)s is already taken. Please try again', username=username.data))
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).filter_by(email = email.data.lower()))

        if user is not None:
            raise ValidationError(_('%(email)s is already taken. Please use another email or reset password', email=email.data))
    
    def validate_password(self, password):
        special_chars = '!@#$%^&-_'
        valid_chars = ascii_uppercase+ascii_lowercase+digits+special_chars
        if password.data.find(self.username.data)>=0:
            raise ValidationError(_('Password is not allowed to contain your username.'))
        if not re.search('([!@#$%^&-_]+)',password.data):
            raise ValidationError(_('Password needs to have at least one special character from [%(special_chars)s]', special_chars=special_chars))
        if not re.search('[A-Z]',password.data):
            raise ValidationError(_('Password must contain at least 1 Upper Case (Capital) letter'))
        if not re.search('[0-9]', password.data):
            raise ValidationError(_('Password must contain at least 1 number'))
        if not re.search('[a-z]', password.data):
            raise ValidationError(_('Password must contain at least 1 lower case letter'))

class EditProfileForm(FlaskForm):

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About Me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def validate_username(self, username):
        if username.data != self.original_username: 
            user = db.session.scalar(sa.select(User).filter_by(username=username.data))
            if user is not None:
                raise ValidationError(_('Username already exists! Please choose another name'))
            
class EmptyForm(FlaskForm):
    submit = SubmitField(_l("Submit"))

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