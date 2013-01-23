from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.core.validators import email_re
import re
from django import http
from django.template import Context, RequestContext, loader

# Create your views here.

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """

    ctx = {}
    if request.user.is_authenticated():
        ctx['site_base']= "new_site_base.html"
    else:
        ctx['site_base']= "site_registration_base.html"

    t = loader.get_template(template_name)
    return http.HttpResponseServerError(t.render(RequestContext(request, ctx)))
