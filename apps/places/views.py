from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from mydebug import *
from models import *
import re
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse




def view_school(request, school_id, **kwargs):
    
    if not re.match('^[0-9]+$',school_id): # user id    
        raise Exception("Invalid School")
  
    if request.user.is_authenticated():
        template='schools/view_school_user.html'
    else:
        template='schools/view_school_non_user.html'


    ctx = { }

 
    return render_to_response(template, RequestContext(request, ctx))




@login_required
def delete_location(request);
    if request.method == "POST":
        id = request.POST.get("id", None)

        if not re.match('^[0-9]+$',id): # user id    
            raise Exception('bad id')

        lo = Place.objects.get(id=id, owner=request.user)
        lo.delete()

        response_dict = { "success":True, "message": "Done" }
    
        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')


@login_required
def save_location(request):
    if request.method == "POST":
        name = request.POST.get("name", None)
        address = request.POST.get("address", None)
        lo = Place(owner=request.user, name=name, address=address)
        lo.save()

        response_dict = { "success":True, "message": "Done", "id":lo.id }
    
        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')

