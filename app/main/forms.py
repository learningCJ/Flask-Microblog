from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_babel import lazy_gettext as _l, _
from app import db
from app.models import User
import sqlalchemy as sa

class AboutSiteForm(FlaskForm):
    techType = StringField(_('Tech Type'), validators=[DataRequired(), Length(min=1, max=50)])
    techName = StringField(_('Tech Name'), validators=[DataRequired(), Length(min=1, max=100)])
    category = SelectField(_('Category'), choices=[('Software'), ('Infrastructure')])
    submit = SubmitField(_l('Submit'))

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