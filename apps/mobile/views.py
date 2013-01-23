from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
import time

from mydebug import *

from django.http import HttpResponse, Http404


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def setstatus(request, **kwargs):

    params = None
    status = 'Send us your update. Ex: "Going to the park with Frankie. Going to be there until 2pm'


    if request.method == "GET" and "set_status" in request.GET:
        params = request.GET
    elif request.method == "POST" and "set_status" in request.POST:
        params = request.POST

    if params is not None:
        status = params["set_status"]

    return HttpResponse("<message><content>Thanks! "+str(status)+"</content></message>")
