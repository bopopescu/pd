from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from models import *
from forms import *
from mydebug import *
import re
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse

from models import *

from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()


def view_album(request, album_id):
    album = Album.objects.get(id=album_id)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            np = Photo(caption=form.cleaned_data["title"], original_image=request.FILES['file'])
            np.save()
            set_profile_pic = False
            if album.photos:
                set_profile_pic = True
            
            album.add(np)
            
    else:
        form = UploadFileForm()
    
    return render_to_response('view_album.html', {'album':album, 'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            np = Photo(caption=form.cleaned_data["title"], original_image=request.FILES['file'])
            np.save()
    else:
        form = UploadFileForm()

    return render_to_response('upload.html', {'form': form})


def view_photo(request, photo_id):
    photo_owner = 
# discrete unit of ownership for a photo?
# multiple ownership?
# playdate photos belong to?
# display photos for a child?
# display photos for a parent?

# is it access path dependent?
# I am viewing photos for child_id 1 and i can acess photos for child_id 1 and child_id 1 is the owner of the album for this photo or in this photo
# I am viewing photos for playdate_id 1 and i can see photos for playdate_id1 and this photo is in an album for playdate_id1
# next, previous buttons - next what exactly? previous what exactly?

# you need to tell me why you should have access to this photo for me to let you see it




    return True

def view_album(request, album_id):






    return True


