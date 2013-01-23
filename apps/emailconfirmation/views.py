from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from emailconfirmation.models import EmailConfirmation
from notify.models import send_email

def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)

    if email_address is not None:
        request.session["message"] = 'You have verified ' + str(email_address.email) + ' as  your address.'
        send_email(email_address.email, 'welcome_email', ctx = { 'actor':email_address.user.get_profile() }, skip_footer=True)
    else:
        request.session["message"] = 'Invalid confirmation key.'

    return HttpResponseRedirect(reverse("acct_login"))
