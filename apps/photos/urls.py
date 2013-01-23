from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import * 

urlpatterns = patterns('',
     url(r"^upload_form", "photos.views.upload_file", name="image_upload_form"),
     url(r"^album/(?P<album_id>\d+)/$", "photos.views.view_album", name="view_album"),
     url(r"^photo/(?P<photo_id>\d+)/$", "photos.views.view_photo", name="view_photo"),
     url(r"^photo/(?P<photo_id>\d+)/delete$", "photos.views.delete_photo", name="delete_photo"),
     url(r'^upload/(?P<album_id>\d+)/$', 'photos.views.upload_file', name='uploadify_upload'),
     url(r'^upload_done/(?P<album_id>\d+)/$', 'photos.views.upload_done', name='upload_done'),
     url(r'^upload/$', 'photos.views.upload_file', name='uploadify_upload'),
     url(r'^share_fb$', 'photos.views.share_fb', name='share_fb' ),
     url(r'^photo/(?P<photo_id>\d+)/make_profile_pic$', 'photos.views.make_profile_pic', name='make_profile_pic' ),
)
