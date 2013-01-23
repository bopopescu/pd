from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from models import *
from places.models import Zip
from photos.models import get_photos_for_children
from mydebug import *
import urllib, simplejson
from my_django_utils import PDEncoder, children_required

from django.contrib import messages

@login_required
def my_profile(request, **kwargs):


    ctx = {
        'profile':request.user.get_profile()
    }
    
    
    template = "profiles/my_profile.html"
    return render_to_response(template, RequestContext(request, ctx))

@login_required
@children_required
def view(request, user_id = None, **kwargs):

#    messages.add_message(request, messages.INFO, 'a message')

    me = False
    if user_id is None:
        user = request.user
        me = True
    else:
        user = User.objects.select_related('_profile_cache').get(id=user_id)
        if user == request.user:
            me = True

    # request.owner's children (for adding to playlist)

    # owner of currently viewed profile display children

    manage_playlist_children = get_cv_list_from_ac(request.user, request.user.get_profile().manage_playlist_children)

    
    display_children = get_cv_list_from_ac(request.user, user.get_profile().display_children)  

    view_playlist_children = []

    # those owner display children whose playlists we can see
    for cv in display_children:
        if cv.can_view_child_playlist:
            view_playlist_children.append(cv)

    view_photos_children = []
    for cv in display_children:
        if cv.can_view_child_photos:
            view_photos_children.append(cv.child)

    photos = []
    if len(view_photos_children):
        photos = get_photos_for_children(view_photos_children, 3)

    ctx = {
        'profile':user.get_profile(),
        'display_children':display_children,
        'view_playlist_children':view_playlist_children,
        'manage_playlist_children':manage_playlist_children,
        'photos':photos,
        'me': me,
        'cat_profile':True,
    }
    
    template = "profiles/view_profile.html"
    return render_to_response(template, RequestContext(request, ctx))

@login_required
def profile_in_place_save(request):
    if request.method == "POST":
        f = request.POST.get("field");
        v = request.POST.get("value");
        if v == 'false':
            v = False
        elif v=='true':
            v = True

        valid_fields = { 'about':True, 'phone':True, 'location':True }
        if not f in valid_fields:
            raise Exception('invalid field' + f)

        profile = request.user.get_profile()
        response_dict = {}

        if f == 'location':
            new_zip = v
            if not re.match('^[0-9]+$',new_zip):
                response_dict = { "success":False, "message":"Invalid Zip Code"}
            else:
                try:
                    new_zc = Zip.objects.get(zip=new_zip)
                    profile.zip_code = new_zc
                    profile.save()
                    response_dict = { "success":True, "new_location": new_zc.city + ',' + new_zc.state, "new_zip":new_zc.zip }
                except Zip.DoesNotExist:
                    response_dict = { "success":False, "message":"Invalid Zip Code"}
        else:            
            if hasattr(profile, f):
                setattr(profile, f, v)
                profile.save()
            else:
                raise Exception('invalid field' + f)
        
            response_dict = { "success":True, "message": "Done" }

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@login_required
def child_in_place_save(request, child_id):
    child = None
    if not re.match('^[0-9]+$',child_id):
        raise Exception('Invalid input')
    try:
        child = Child.objects.select_related('album','photo','school').get(id=child_id)
    except Child.DoesNotExist:
        raise Exception("Invalid input")

    cv = ChildView(user=request.user, child=child)
    if not cv.is_child_mine:
        raise Exception("You do not have permissions for this")
    
    if request.method == "POST":
        f = request.POST.get("field");
        v = request.POST.get("value");
        if v == 'false':
            v = False
        elif v=='true':
            v = True

        valid_fields = { 'places':True, 'toys':True, 'shows':True, 'foods':True, 
                         'diet':True, 'sports':True, 'activies':True, 'languages':True, 'playdate_requirements':True,
                         'grade_level':True, 'school_id':True, 'summer_camp':True, 'about':True, }
        if not f in valid_fields:
            raise Exception('invalid field' + f)
        if f == 'school_id':
            school = School.objects.get(id=v)
            child.school = school
            child.save()
        elif hasattr(child, f):
            setattr(child, f, v)
            child.save()
        else:
            raise Exception('invalid field' + f)
    
        response_dict = { "success":True, "message": "Done" }

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

@login_required
@children_required
def view_child_profile(request, child_id, **kwargs):

    child = Child.objects.select_related('photo','album','school').get(id=child_id)
    
    cv = ChildView(user=request.user, child=child)
    if not cv.can_view_child_extended_profile:
        raise Exception('No permissions to view this child\'s profile page')

    photos = None    
    if cv.can_view_child_photos:
        photos = get_photos_for_children([ child ], 3)


    ctx = {        
        'childview':cv,
        'can_edit_profile': cv.can_edit_child_playlist,
        'can_view_calendar': cv.can_view_child_schedule,
        'key':cv.key(),
        'my_child':cv.is_child_mine,
        'photos':photos,
    }

    
    template = "profiles/child_profile.html"
    return render_to_response(template, RequestContext(request, ctx))



from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50, required=False)
    file  = forms.FileField()


def view_user_album(request, user_id = None):
    if user_id is None:
        user = request.user
        me = True
    else:
        user = User.objects.select_related('_profile_cache').get(id=user_id)
        if user == request.user:
            me = True

    album = user.get_profile().album

    if request.method == 'POST':
        if not me:
            raise Exception("You can not upload photos to this profile")

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            np = Photo(album=album, caption=form.cleaned_data.get("title","Profile"), original_image=request.FILES['file'])
            np.save()
            set_profile_pic = False
            if not album.photos.all():
                set_profile_pic = True
            else:
                pass
                          
            if set_profile_pic:
                request.user.get_profile().set_profile_pic(np)            
            
    form = UploadFileForm()

    ctx = {
        'me':me,
        'album':album,
        'photo_form':form,
    }

    template = "profiles/user_profile_album.html"
    return render_to_response(template, RequestContext(request, ctx))


def view_child_photos(request, child_id):
    if not re.match('^[0-9]+$',child_id):
        raise Exception('Invalid input')
    try:
        child = Child.objects.select_related('album','photo','school').get(id=child_id)
    except Child.DoesNotExist:
        raise Exception("Invalid input")

    cv = ChildView(user=request.user, child=child)
    if not cv.can_view_child_photos:
        raise Exception("You do not have permissions for this")

    album = child.album

    if request.method == 'POST':
        if not cv.can_upload_child_photos:
            raise Exception("You can not upload photos for this child")

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            np = Photo(album=album,caption=form.cleaned_data.get("title","Profile"), original_image=request.FILES['file'])
            np.save()
            set_profile_pic = False
            if not album.photos.all():
                set_profile_pic = True
            else:
                pass
                          
            if set_profile_pic:
                child.set_profile_pic(np)            
            
    form = UploadFileForm()

    ctx = {
        'childview': cv,
        'album':album,
        'photo_form':form,
    }

    template = "profiles/child_profile_album.html"
    return render_to_response(template, RequestContext(request, ctx))
	
            
def set_got_fb_stream_publish(request):
    profile = request.user.get_profile()
    profile.fb_stream_publish = True
    profile.save()
    
    response_dict = { "success":True, "message": "Done" }
    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
    

def get_fb_status(request):
    response = {}
    response["got_fb"] = False
    response["got_fb_perms"] = False

    if request.user.get_profile().fb_account_linked:
        response["got_fb"] = True

    if request.user.get_profile().fb_stream_publish:
        response["got_fb_perms"] = True

    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')
