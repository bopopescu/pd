from django.utils.text import wrap
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.template import Context, loader
from django.template.loader import render_to_string
from django.conf import settings

# favour django-mailer but fall back to django.core.mail

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

def format_quote(text):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(text, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    return '\n'.join(lines)