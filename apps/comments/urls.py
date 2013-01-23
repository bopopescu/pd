from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


from views import *

urlpatterns = patterns('',                                          
    url(r"^new", "comments.views.new_comment", name="new_comment"),
    url(r"^list", "comments.views.list_comments", name="list_comments"),
)

