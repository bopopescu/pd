from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib.auth import login

from account.signals import user_logged_in

from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode
from htmlentitydefs import name2codepoint
# from satchmo_utils import random_string
import re
import unicodedata
import random

_is_alnum_re = re.compile(r'\w+')
_ID_MIN_LENGTH = 5  # minimum reasonable length for username
_ID_MAX_LENGTH = 30 # as defined in django.auth.contrib.models.User.username field

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


LOGIN_REDIRECT_URLNAME = getattr(settings, "LOGIN_REDIRECT_URLNAME", "")


def get_default_redirect(request, redirect_field_name="next",
        login_redirect_urlname=LOGIN_REDIRECT_URLNAME, session_key_value="redirect_to"):
    """
    Returns the URL to be used in login procedures by looking at different
    values in the following order:
    
    - a REQUEST value, GET or POST, named "next" by default.
    - LOGIN_REDIRECT_URL - the URL in the setting
    - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the settings
    """
    if login_redirect_urlname:
        default_redirect_to = reverse(login_redirect_urlname)
    else:
        default_redirect_to = settings.LOGIN_REDIRECT_URL
    from mydebug import *
    redirect_to = request.REQUEST.get(redirect_field_name)
    if not redirect_to:
        # try the session if available
        if hasattr(request, "session"):
            redirect_to = request.session.get(session_key_value)
    # light security check -- make sure redirect_to isn't garabage.
    if not redirect_to or "://" in redirect_to or " " in redirect_to:
        redirect_to = default_redirect_to
    return redirect_to


def user_display(user):
    func = getattr(settings, "ACCOUNT_USER_DISPLAY", lambda user: user.username)
    return func(user)

def perform_login(request, user):
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    login(request, user)



def _id_generator(first_name, last_name, email):
    def _alnum(s, glue=''):
        return glue.join(filter(len, _is_alnum_re.findall(s))).lower()
    # The way to generate id is by trying:
    #  1. username part of email
    #  2. ascii-transliterated first+last name
    #  3. whole email with non-alphanumerics replaced by underscore
    #  4. random string
    # Every try must return at least _ID_MIN_LENGTH chars to succeed and is truncated
    # to _ID_MAX_LENGTH. All IDs are lowercased.
    id = _alnum(email.split('@')[0])
    if len(id) >= _ID_MIN_LENGTH:
        yield id[:_ID_MAX_LENGTH]
    id = _alnum(unicodedata.normalize('NFKD', unicode(first_name + last_name)).encode('ascii', 'ignore'))
    if len(id) >= _ID_MIN_LENGTH:
        yield id[:_ID_MAX_LENGTH]
    id = _alnum(email, glue='_')
    if len(id) >= _ID_MIN_LENGTH:
        yield id[:_ID_MAX_LENGTH]
    while True:
        yield _alnum('%s_%s' % (id[:_ID_MIN_LENGTH], random_string(_ID_MIN_LENGTH, True)))[:_ID_MAX_LENGTH]

def generate_id(first_name='', last_name='', email=''):
    valid_id = False
    gen = _id_generator(first_name, last_name, email)
    test_name = gen.next()
    while valid_id is False:
        try:
            User.objects.get(username=test_name)
        except User.DoesNotExist:
            valid_id = True
        else:
            test_name = gen.next()
    return test_name

# From http://www.djangosnippets.org/snippets/369/
def slugify(s, entities=True, decimal=True, hexadecimal=True,
   instance=None, slug_field='slug', filter_dict=None):
    s = smart_unicode(s)

    #character entity reference
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

    #decimal character reference
    if decimal:
        try:
            s = re.sub('&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass

    #hexadecimal character reference
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);', lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass

    #translate
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

    #replace unwanted characters
    #Added _ because this is a valid slug option
    s = re.sub(r'[^-a-z0-9_]+', '-', s.lower())

    #remove redundant -
    s = re.sub('-{2,}', '-', s).strip('-')

    slug = s
    if instance:
        def get_query():
            query = instance.__class__.objects.filter(**{slug_field: slug})
            if filter_dict:
                query = query.filter(**filter_dict)
            if instance.pk:
                query = query.exclude(pk=instance.pk)
            return query
        counter = 1
        while get_query():
            slug = "%s-%s" % (s, counter)
            counter += 1
    return slug


def random_string(length, variable=False, charset=_LETTERS):
    if variable:
        length = random.randrange(1, length+1)
    return ''.join([random.choice(charset) for x in xrange(length)])
