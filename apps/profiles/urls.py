from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns("",
    url(r"^view/(?P<user_id>\d+)/$", "profiles.views.view", name="view_profile"),
    url(r"^view/$", "profiles.views.view", name="view_profile"),
    url(r"^view/profile_in_place_save/$", "profiles.views.profile_in_place_save", name="profile_in_place_save"),
    url(r"^view/child/(?P<child_id>\d+)/child_in_place_save/$", "profiles.views.child_in_place_save", name="child_in_place_save"),

    url(r"^view/child/(?P<child_id>\d+)/$", "profiles.views.view_child_profile", name="view_child"),
    url(r"^set_got_fb_stream_publish/$", "profiles.views.set_got_fb_stream_publish", name="flag_fb_stream_publish"),
    url(r"^view/user/album/$", "profiles.views.view_user_album", name="view_user_album"),
    url(r"^view/child/(?P<child_id>\d+)/album/$", "profiles.views.view_child_photos", name="view_child_photos"),
    url(r"^view/user/album/(?P<user_id>\d+)/$", "profiles.views.view_user_album", name="view_user_album"),
    url(r"^get_fb_status/$", "profiles.views.get_fb_status", name="get_fb_status"),

)

