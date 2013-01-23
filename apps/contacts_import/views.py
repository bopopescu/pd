from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required

from gdata.contacts.service import ContactsService

from contacts_import.forms import VcardImportForm
from contacts_import.backends.importers import GoogleImporter, YahooImporter, GenericImporter, EmailListImporter
from contacts_import.settings import RUNNER, CALLBACK
import cgi
import oauth2 as oauth
from mydebug import *
import urllib, simplejson
import time

GOOGLE_CONTACTS_URI = "http://www.google.com/m8/feeds/"


@login_required
def import_contacts(request, type):
    runner_class = RUNNER
    callback = CALLBACK

    import_id = int(time.time())

    if type == "yahoo":
        yahoo_token = request.session.pop("yahoo_token", None)
        if yahoo_token:
            runner = runner_class(YahooImporter,
                user = request.user,
                yahoo_token = yahoo_token,
                import_id = import_id,
            )
            results = runner.import_contacts()
    
    elif type == "google":
        authsub_token = request.session.pop("authsub_token", None)
        if authsub_token:
            runner = runner_class(GoogleImporter,
                user = request.user,
                authsub_token = authsub_token,
                import_id = import_id,
            )
            results = runner.import_contacts()

    elif type == "generic":
        generic = request.session.pop("generic", None)
        email=request.session.pop("email", None)
        password=request.session.pop("password", None)         
        runner = runner_class(GenericImporter,
            user = request.user,
            email=email,
            password=password,
            import_id = import_id,            
        )
        results = runner.import_contacts()
    elif type == "email_list":
        email_list = request.session.pop("email_list", None)
        runner = runner_class(EmailListImporter,
            user = request.user,
            email_list = email_list,
            import_id = import_id,
            send_invites = True,
        )
        results = runner.import_contacts()
    else:
        raise Exception('Invalid import type')

        
    return results


def authsub_login(request):
    if "token" in request.GET:
        request.session["authsub_token"] = request.GET["token"]
        return render_to_response("account/imported.html", RequestContext(request, {}))

    contacts_service = ContactsService()
    authsub_url = contacts_service.GenerateAuthSubURL(request.build_absolute_uri(), GOOGLE_CONTACTS_URI, False, True)

    return HttpResponseRedirect(authsub_url)

def yahoo_login(request):
    
    consumer = oauth.Consumer(settings.YAHOO_CONSUMER_KEY, settings.YAHOO_CONSUMER_SECRET)

    if request.GET == {}:
        client = oauth.Client(consumer)
        callback_url = 'http://'+settings.WWW_HOST+'/contacts/yahoo/login'
        request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
               
        resp, content = client.request(request_token_url, method="GET", callback_url=callback_url)
       
        response_dict = dict(cgi.parse_qsl(content))

        if ((str(resp['status']) != '200') or ('oauth_problem' in response_dict)):
            raise Exception("CANT GET REQUEST TOKEN"+str(response_dict))
        
        request.session['yahoo_token'] = response_dict
    
        authenticate_url = 'https://api.login.yahoo.com/oauth/v2/request_auth'    

        url = "%s?oauth_callback=%s&oauth_token=%s" % (authenticate_url, callback_url, request.session['yahoo_token']['oauth_token'])
        return HttpResponseRedirect(url)

    elif request.GET['oauth_verifier'] != '':
        verifier = request.GET['oauth_verifier']
        token = oauth.Token(request.session['yahoo_token']['oauth_token'],request.session['yahoo_token']['oauth_token_secret'])
        token.set_verifier(verifier)
        client = oauth.Client(consumer, token)
        access_token_url='https://api.login.yahoo.com/oauth/v2/get_token'
        resp, content = client.request(access_token_url, "GET")
        if str(resp['status']) != '200':
            raise Exception("CANT GET ACCESS TOKEN")
        access_token = dict(cgi.parse_qsl(content))

        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

        request.session['yahoo_token'] = token.to_string()

    return render_to_response("account/imported.html", RequestContext(request, {}))

#    return HttpResponseRedirect(redirect_to)
    
def invite_email(request):
    return render_to_response("contacts_import/import_contacts.html", RequestContext(request, {}))

def invite_facebook(request):
    return render_to_response("contacts_import/import_facebook.html", RequestContext(request, { 'fb_app_id': settings.FB_API_KEY, 'www_host': settings.WWW_HOST }))


def signup_run_import(request):

    if 'yahoo_token' in request.session:
        type='yahoo'
    elif 'authsub_token' in request.session:        
        type='google'
    elif 'generic' in request.session:
        type='generic'
    elif 'email_list' in request.session:
        type='email_list'
    else:
        # noop
        return True, None

    error = None
    status = True
    try:
        result = import_contacts(request, type)        
    except Exception as inst:
        from django_open_inviter.exceptions import LoginFailed, InvalidService
        if isinstance(inst, LoginFailed):
            error = 'Login Failed'
            status = False
        elif isinstance(inst, InvalidService ):
            error = 'Invalid Email Service'
            status = False
        else:
            pass
    return (status, error)
