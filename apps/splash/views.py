from django.conf import settings
from models import WaitingList
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
# from django.forms.fields import email_re
from django.core.validators import email_re
import re

# Create your views here.

def is_valid_email(email):
    return True if email_re.match(email) else False


def splash(request, **kwargs):

    template_name = 'splash/splash.html'

    if request.method == "POST":

        errors = []
        errors_ctx = { }
        email = (request.POST["email"])
        email = email.lower();
        if not is_valid_email(email):
            errors.append('Please enter a valid email address')
        else:
            errors_ctx.update({ 
                'email':email
            })

        zip_code = request.POST["zip_code"] 
        if not (re.match('^[0-9]{5}$',zip_code) or re.match('^\w\d\w\s?\d\w\d$',zip_code)):
            errors.append('Please enter a valid zip code or postal code ')
        else:
            errors_ctx.update({ 
                'zip_code':zip_code
            })

        if not errors:
            wl = WaitingList(email=email, zip_code=zip_code)
            wl.save()
            errors_ctx = { 'submitted':'1' }
        else:
            errors_ctx.update({
                'submitted':'1',
                'errors':errors,
            })


        return render_to_response(template_name, errors_ctx)

    return render_to_response(template_name, {} )
