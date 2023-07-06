from wtforms.validators import  ValidationError
import json
import re
from flask_babel import lazy_gettext as _l
from flask_babel import _

def pwPolicy(form, field):
    f = open ('pwConfig.json', "r")
    pwConfig = json.loads(f.read())

    special_chars = pwConfig["pwSpecialCharREGEX"]
    
    if not re.search(special_chars,field.data):
        raise ValidationError(_('Password needs to have at least one special character from %(special_chars)s', special_chars=special_chars.replace('\\','')[1:-1]))
    if not re.search('[A-Z]',field.data):
        raise ValidationError(_('Password must contain at least 1 Upper Case (Capital) letter'))
    if not re.search('[0-9]', field.data):
        raise ValidationError(_('Password must contain at least 1 number'))
    if not re.search('[a-z]', field.data):
        raise ValidationError(_('Password must contain at least 1 lower case letter'))