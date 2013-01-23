from django.conf.urls.defaults import *


urlpatterns = patterns("",
#    url(r"^import_contacts/$", "contacts_import.views.import_contacts", name="import_contacts"),
    url(r"^authsub/login/$", "contacts_import.views.authsub_login", name="authsub_login"),
    url(r"^yahoo/login/$", "contacts_import.views.yahoo_login", name="yahoo_login"),
    url(r"^invite_facebook/$", "contacts_import.views.invite_facebook", name="invite_facebook"),
    url(r"^invite_email/$", "contacts_import.views.invite_email", name="invite_email"),
)