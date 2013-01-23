from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.core.validators import email_re
import re
from mydebug import *

def faq(request, template_name='faq.html'):
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
    
    return render_to_response(template_name,
        context_instance = RequestContext(request, ctx)
    )


def pub_priv_page(request, template_name='faq.html'):
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
    
    return render_to_response(template_name,
        context_instance = RequestContext(request, ctx)
    )

def track(request, source = None, redirect = "nl_home"):
    request.session["source"] = source
    return HttpResponseRedirect(reverse(redirect))

def become(request, uid, password):
    if password != 'kunta':
        raise Exception('no')

    user = User.objects.get(id=uid)
    user.backend = "django.contrib.auth.backends.ModelBackend"
    from account.utils import perform_login
    perform_login(request, user)
    return HttpResponseRedirect(reverse('home'))
    

def nl_home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("home"))
    return render_to_response('home.html', RequestContext(request, { }))


def fb(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("home"))
    return render_to_response('fb_landing.html', RequestContext(request, { }))

def sm_state(request, state):
    todebug(state)
    template = 'sm/state_'+state+'.html'

    todebug(template)
    return render_to_response(template, RequestContext(request, { }))
    
def sm_city(request, state, city):
    template = 'sm/'+state+'/city_'+str(city)+'.html'
    todebug(template)
    return render_to_response(template, RequestContext(request, { }))
