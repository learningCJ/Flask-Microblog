import re
from hashlib import md5

def text_linkification(text_to_convert):
    converted_text = text_to_convert
    URLRegex="http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#!%]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    URLsinBody = set(re.findall(URLRegex, converted_text))
    for URLinBody in URLsinBody:
            converted_text = converted_text.replace(URLinBody, f'<a href="{URLinBody}" target="_blank">{URLinBody}</a>')
    return converted_text

def anonymous_avatar(size, email):
    digest = md5(email.lower().encode('utf-8')).hexdigest()
    return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest,size)