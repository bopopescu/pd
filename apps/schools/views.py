from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from mydebug import *
from models import *
from profiles.models import *
import re
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
import urllib, simplejson




def view_school(request, school_id, **kwargs):
    
    if not re.match('^[\w]+$',school_id): # user id    
        raise Exception("Invalid School")

    school = School.objects.get(id = school_id)
    parents_ac = list(Adult_Child.objects.select_related('adult','adult___profile_cache','child', 'adult___profile_cache__photo', 'adult___profile_cache__zip_code').cache().filter(child__school=school)[:15])

    parents = []
    parent_seen = {}
    for ac in parents_ac:
        profile = ac.adult.get_profile()
        if profile.school_display:
            if not str(profile.id) in parent_seen:
                parents.append(profile.get_profile())
                parent_seen[str(profile.id)] = True

    if request.user.is_authenticated():
        template='schools/view_school_user.html'
    else:
        template='schools/view_school_non_user.html'

    ctx = { 'school':school, 'parents':parents, 'www_host':settings.WWW_HOST }

 
    return render_to_response(template, RequestContext(request, ctx))

def search_school_zip(request):
    if request.user.is_authenticated():
        q = request.GET.get("q")
        zip = request.user.get_profile().zip_code

        if not re.match('^[\w\s\.\-\']+$',q):
            raise Exception('Invalid input')

        zsp_qs = Zip_School_Prox.objects.cache().filter(zip=zip).all()

        response = []
        schools = []
        for zsp in zsp_qs:
            if re.match("^"+q,zsp.name, re.IGNORECASE):
                schools.append(zsp.school_id)
                
        school_qs = School.objects.cache().filter(id__in=schools).all()

        for sch in school_qs:
                response.append({
                                 'value': sch.id,
                                 'label': sch.name + "(" + sch.city + "," + sch.state + ")",
                                 })

        return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')
