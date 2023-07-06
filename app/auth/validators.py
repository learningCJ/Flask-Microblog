from wtforms.validators import  ValidationError
import json
import re
from flask_babel import lazy_gettext as _l
from flask_babel import _

def pwPolicy(form=None, field=None, data=None):
    f = open ('pwConfig.json', "r")
    pwConfig = json.loads(f.read())

    if data == None:
        data = field.data

    pwMinLen = pwConfig["pwMinLen"]
    pwLenREGEX = pwConfig["pwMinLenREGEX"]
    special_chars = pwConfig["pwSpecialCharREGEX"]
    capitalREGEX = pwConfig["pwUpperCaseREGEX"]
    numREGEX = pwConfig["pwNumREGEX"]
    lowercaseREGEX = pwConfig["pwLowerCaseREGEX"]
    
    if not re.search(pwLenREGEX, data):
        raise ValidationError(_('Password must contain at least %(pwMinLen)d characters', pwMinLen=pwMinLen ))
    if not re.search(special_chars,data):
        raise ValidationError(_('Password needs to have at least one special character from %(special_chars)s', special_chars=special_chars.replace('\\','')[1:-1]))
    if not re.search(capitalREGEX,data):
        raise ValidationError(_('Password must contain at least 1 Upper Case (Capital) letter'))
    if not re.search(numREGEX, data):
        raise ValidationError(_('Password must contain at least 1 number'))
    if not re.search(lowercaseREGEX, data):
        raise ValidationError(_('Password must contain at least 1 lower case letter'))