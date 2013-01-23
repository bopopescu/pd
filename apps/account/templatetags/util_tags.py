from django import template
from django.conf import settings

from mydebug import *

register = template.Library()


@register.filter
def key(d, key_name):
    try:
        value = d[key_name]
    except KeyError:
        value = ''

    return value
key = register.filter('key', key)

def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endraw'
    tolog("in raw tag")
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)
raw = register.tag(raw)


class VerbatimNode(template.Node):
    def __init__(self, text):
        self.text = text
    
    def render(self, context):
        return self.text


def verbatim(parser, token):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim':
            break
        if token.token_type == template.TOKEN_VAR:
            text.append('{{')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('{%')
        text.append(token.contents)
        if token.token_type == template.TOKEN_VAR:
            text.append('}}')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('%}')
    return VerbatimNode(''.join(text))
verbatim = register.tag(verbatim)


def google_anal_account():
    return settings.GOOGLE_ANAL_ACCOUNT

def www_host():
    return settings.WWW_HOST

def fb_app_id():
    return settings.FB_API_KEY

register.simple_tag(google_anal_account)
register.simple_tag(www_host)
register.simple_tag(fb_app_id)
