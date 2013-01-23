from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from models import *
from mydebug import *
import re
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from my_django_utils import PDEncoder

from models import *
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
import urllib, simplejson
import traceback

@login_required
def view_album(request, album_id):
    album = Album.objects.cache().select_related('owner','created_by','created_by___profile_cache').get(id=album_id)

    if not album.can_view_album(request.user):
        raise Exception('unauthorized to view')

    can_upload = False
    if album.can_upload_photo(request.user):
        can_upload = True

    photos = get_photos_from_album(request, album)

    upload_url = reverse("upload_done", kwargs={"album_id":album.id})
    
    ctx = {'album':album, 'photos':photos, 'can_upload': can_upload, 'upload_url': upload_url, 'session_key': request.session.session_key }
    
    return render_to_response('photos/view_album.html', RequestContext(request, ctx))

@login_required
def get_photos_from_album(request, album):
    all_photos = Photo.objects.select_related('album','album__owner').filter(album=album) 
#    album.photos.cache().select_related('album','album__owner').all()
    photos = []
    for ph in all_photos:
#        photos.append(ph)
        if ph.can_view_photo(request.user):
            photos.append(ph)

    return photos

@login_required
def view_photo(request, photo_id):

    photo = Photo.objects.select_related('album','album__owner').get(id=photo_id)
    if not photo.can_view_photo(request.user):
        raise Exception('unauthorized')

    pi = photo.album.owner.photo_id
    
    profile_pic = False

    if pi is not None and str(pi) == str(photo.id):
        profile_pic = True

    photos = get_photos_from_album(request, photo.album)

    prv = None
    nxt = None

    try:
        ind = photos.index(photo)
    except ValueError:
        ind = None

    if not ind == 0:
        prv = photos[ind-1]

    if not ind == len(photos)-1:
        nxt = photos[ind+1]

    can_delete = False
    if not profile_pic:
        can_delete = photo.can_delete_photo(request.user)

    can_set_profile = photo.album.can_upload_photo(request.user)
    set_profile_language = photo.album.owner.set_profile_language()

    ctx = { 'photo':photo, 
            'album':photo.album, 
            'prev': prv, 
            'next': nxt, 
            'owner':photo.album.owner, 
            'profile_pic':profile_pic, 
            'fb_app_id': settings.FB_API_KEY, 
            'can_set_profile':can_set_profile, 
            'can_delete':can_delete,
            'set_profile_language':set_profile_language,
          }
    
    return render_to_response('photos/view_photo.html', RequestContext(request, ctx))
    

@csrf_exempt
def upload_file(request, album_id = None, **kwargs):

    if album_id is None:
        raise Exception('No Album')

    album = Album.objects.get(id=album_id)

    if request.method == 'POST':
        session_key = request.POST.get('session_key',None)

        if session_key is None:
            raise Exception('No session key')
        else:
            from django.contrib.sessions.backends.db import SessionStore
            from account.auth_backends import AuthenticationBackend
            s = SessionStore(session_key=session_key)
            user_id = s['_auth_user_id']
            ab = AuthenticationBackend()
            user = ab.get_user(user_id)
            if not album.can_upload_photo(user):
                raise Exception('user can not upload')

        if request.FILES:
            caption = ''
            if "caption" in request.POST:
                caption = request.POST["caption"]

            fl = request.FILES['Filedata']

# working with a InMemoryUploadedFile class file

            import time
            new_file_name = str(album_id) + '_' +  str(time.time()) + '_' + fl.name
            fl._set_name(new_file_name)

            set_profile_pic = False
            if not album.photos.all():
                set_profile_pic = True

            np = Photo(album=album, caption=caption, original_image=fl)
            
            np.save()
    
            if set_profile_pic:
                album.owner.set_profile_pic(np)

            return HttpResponse('True')
        return HttpResponse('Not True 1')
    return HttpResponse('Not True 2')



@login_required
def upload_done(request, album_id, **kwargs):
    return HttpResponse('Here')

def delete_photo(request, photo_id):
    photo = Photo.objects.select_related('album','album__owner').get(id=photo_id)
    if not photo.can_delete_photo(request.user):
        raise Exception('unauthorized')

    album_id = photo.album_id
    photo.delete()

    return HttpResponseRedirect(reverse("view_album", kwargs={"album_id":album_id}))



def share_fb(request, **kwargs):

    if request.method == 'POST':
        photo_id = request.POST["photo_id"];
        comment = request.POST["comment"];

        if not re.match('^[0-9]+$',photo_id):
            raise Exception('Invalid input')
   
        photo = Photo.objects.select_related('album','album__owner').get(id=photo_id)
        if not photo.can_view_photo(request.user):
            raise Exception('unauthorized')

        from account.graphapi import GraphAPI
        fb_user = request.user.get_profile().get_facebook_user()

        graph=GraphAPI(fb_user.access_token)

        photo.original_image.open()
        pd = photo.original_image.file

        graph.put_photo(pd.file)

        response_dict = { "success":True, "message": "Done" }
    
        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')
   

def make_profile_pic(request, photo_id, **kwargs):
    photo = Photo.objects.select_related('album','album__owner').get(id=photo_id)

    if photo.album.can_upload_photo(request.user):
        photo.album.owner.set_profile_pic(photo)
        
    return HttpResponseRedirect(reverse("view_photo", kwargs={"photo_id":photo_id}))
