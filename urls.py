from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

handler500 = 'error_pages.views.server_error'


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    url(r'^$', "about.views.nl_home",  name='nl_home' ),
    url(r'^fb', "about.views.fb",  name='fb_landing' ),
    url(r'^readmore.html$', direct_to_template, {'template': 'readmore.html'}, name='readmore' ),
    url(r'^index.html$', direct_to_template, {'template': 'home.html'} ),
    url(r'^index.htm$', direct_to_template, {'template': 'home.html'} ),
    url(r'^splash_about.html$', direct_to_template, {'template': 'splash/splash_about.html' } ),
    url(r"^home/",  include("home.urls")),
    url(r"^admin/invite_user/$", "signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^metrics/", include("metrics.urls")),
    url(r"^account/", include("account.urls")),
    url(r"^account/", include("account.urls")),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^friends/", include("friends.urls")),
    url(r"^messages/", include("notify.urls")),
    url(r"^playdates/", include("playdates.urls")),
    url(r"^schools/", include("schools.urls")),
    url(r"^photos/", include("photos.urls")),
    url(r"^comments/", include("comments.urls")),
    url(r"^schedule/", include("schedule.urls")),
    url(r"^search/", include("search.urls")),
    url(r"^contacts/", include("contacts_import.urls")),
    url(r"^t/(?P<source>\w+)/", "about.views.track", name='track', kwargs={'redirect':'nl_home'} ),
#    url(r"^f/(?P<source>\w+)/", "about.views.track", name='track', kwargs={'redirect':'signup_fb'} ),
    url(r"^f/(?P<source>\w+)/", "about.views.track", name='track', kwargs={'redirect':'fb_landing'} ),
    url(r"^faq.html$", "about.views.pub_priv_page",  name='faq', kwargs={'template_name':'faq.html'} ),
    url(r"^about_us.html$", "about.views.pub_priv_page",  name='about_us', kwargs={'template_name':'about_us.html'} ),
    url(r"^ip_policy.html$", "about.views.pub_priv_page",  name='ip_policy', kwargs={'template_name':'ip_policy.html'} ),
    url(r"^user_agreement.html$", "about.views.pub_priv_page",  name='user_agreement', kwargs={'template_name':'user_agreement.html'} ),
    url(r"^privacy_policy.html$", "about.views.pub_priv_page",  name='privacy_policy', kwargs={'template_name':'privacy_policy.html'} ),
    url(r"^channel.html$", direct_to_template, { 'template':'channel.html'}),
    url(r'^sentry/', include('sentry.web.urls')),
    url(r"^googlef24b4550b6aad473.html$", direct_to_template, { 'template': 'google_prod_verify.html' }),
    url(r"^1uxdwW82Jw5MqevbxR_2_A--.html$", direct_to_template, { 'template': 'yahoo_verify.html' }),
    url(r"^R.v6puBIcD6KgGlQXNo8Tg--.html$", direct_to_template, { 'template': 'yahoo_verify.html' }),
    url(r"^index.cmrl$", direct_to_template, {'template': 'index.cmrl'} ),
    url(r"^google252e5fe81ce1157e.html$", direct_to_template, { 'template': 'googleverify.html' }),
    url(r"^m/", include("mobile.urls")),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/images/favicon.ico'}),
    url(r'^xd_receiver\.html$', direct_to_template, { 'template': 'xd_receiver.html' }),
    url(r'^xd_receiver\.htm$', direct_to_template, { 'template': 'xd_receiver.html' }),
    url(r"^become/(?P<uid>\d+)/(?P<password>\w+)/$", "about.views.become", name="become"),
    url(r"^sm/$", direct_to_template, { 'template': 'sm/states.html' }),
    url(r"^sm/(?P<state>\w+)/$", "about.views.sm_state"),
    url(r"^sm/(?P<state>\w+)/(?P<city>\d+)/$", "about.views.sm_city"),
)



if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
