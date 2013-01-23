from django.conf import settings
from django.conf.urls.defaults import *

from account.forms import SignupForm


#if settings.ACCOUNT_OPEN_SIGNUP:
signup_view = "account.views.signup"
#else:
#    signup_view = "signup_codes.views.signup"


urlpatterns = patterns("",
    url(r"^acct_fb_login", "account.views.account_setup_fb_login", name="fb_login"),
    url(r"^fb_logout", "account.views.fb_logout", name="fb_logout"),
    url(r"^acct_fb_auth", "account.views.account_setup_fb_auth", name="fb_auth"),
    url(r"^signup_add_children", "account.views.add_children", name="signup_add_children", kwargs={'signup': True }),
    url(r"^add_children", "account.views.add_children", name="add_children", kwargs={'signup': False }),

    
    url(r"^signup_connect_fb", "account.views.signup_connect_fb", name="signup_connect_fb"),


    url(r"^connect_fb/pdi/$", "account.views.generic_fb_login", name="connect_fb_pdi", kwargs={'next_handler': 'pdi_fb_auth', 'cancel_handler': 'new_playdate'} ),
    url(r"^auth_fb/pdi/$", "account.views.generic_fb_auth", name="pdi_fb_auth", kwargs={'next_handler': 'new_playdate'} ),

    url(r"^connect_fb/pdip/$", "account.views.generic_fb_login", name="connect_fb_pdip", kwargs={'next_handler': 'pdip_fb_auth', 'cancel_handler': 'new_playdate', 'perms': settings.FB_LOGIN_PERMS_PUBLISH } ),
    url(r"^auth_fb/pdip/$", "account.views.generic_fb_auth", name="pdip_fb_auth", kwargs={'next_handler': 'new_playdate'} ),
    
    url(r"^connect_fb/set/$", "account.views.generic_fb_login", name="settings_fb_login", kwargs={'next_handler': 'settings_fb_auth', 'cancel_handler': 'settings_account'} ),
    url(r"^auth_fb/set/$", "account.views.generic_fb_auth", name="settings_fb_auth", kwargs={'next_handler': 'settings_account'} ),

    url(r"^connect_fb/pht/(?P<arg_name>\w+)/(?P<arg_id>\d+)/$", "account.views.generic_fb_login", name="settings_fb_login", kwargs={'next_handler': 'pht_auth', 'cancel_handler': 'view_photo'} ),
    url(r"^auth_fb/pht/(?P<arg_name>\w+)/(?P<arg_id>\d+)/$", "account.views.generic_fb_auth", name="pht_auth", kwargs={'next_handler': 'view_photo'} ),

    
    url(r"^signup_fb_inviter", "account.views.signup_fb_inviter", name="signup_fb_inviter"),
    url(r"^signup_email_inviter", "account.views.signup_email_inviter", name="signup_email_inviter"),
    url(r"^signup_connect_friends", "account.views.signup_connect_friends", name="signup_connect_friends"),
    url(r"^signup_connect_addr_friends", "account.views.signup_connect_addr_friends", name="signup_connect_addr_friends"),

    url(r"^connect_login", "account.views.connect_login", name="connect_login"),

    url(r"^signup_fb", "account.views.signup_fb", name="signup_fb"),
    url(r"^fb_disconnect", "account.views.fb_disconnect", name="fb_disconnect"),

    url(r"^settings/access", "account.views.settings_access", name="settings_access"),
    url(r"^settings/account", "account.views.settings_account", name="settings_account"),
    url(r"^settings/privacy", "account.views.settings_privacy", name="settings_privacy"),
    url(r"^settings/communication", "account.views.settings_communication", name="settings_communication"),

    url(r"^signup_add_address_book", "account.views.signup_add_address_book", name="signup_add_address_book"),
    url(r"^signup_add_address_book", "account.views.signup_add_address_book", name="invitations_contacts"),    

    
    
    url(r"^email/$", "account.views.email", name="acct_email"),

    url(r"^signup/$", signup_view, name="acct_signup"),
    url(r"^signup/(?P<confirmation_key>\w+)/$", "account.views.signup_fb", name="acct_signup_key"),

    url(r"^beta/$", "account.views.beta", name="acct_beta"),

    url(r"^login/$", "account.views.login", name="acct_login"),
    url(r"^login/(?P<msg>\d+)/$", "account.views.login", name="acct_login"),

    url(r"^password_change/$", "account.views.password_change", name="acct_passwd"),
    url(r"^password_set/$", "account.views.password_set", name="acct_passwd_set"),
    url(r"^timezone/$", "account.views.timezone_change", name="acct_timezone_change"),
    url(r"^other_services/$", "account.views.other_services", name="acct_other_services"),
    url(r"^other_services/remove/$", "account.views.other_services_remove", name="acct_other_services_remove"),
#    
    url(r"^language/$", "account.views.language_change", name="acct_language_change"),
    url(r"^logout/$", "django.contrib.auth.views.logout", {"template_name": "account/logout.html"}, name="acct_logout"),
#    
    url(r"^confirm_email/(\w+)/$", "emailconfirmation.views.confirm_email", name="acct_confirm_email"),
#    
#    # password reset
    url(r"^password_reset/$", "account.views.password_reset", name="acct_passwd_reset"),
    url(r"^password_reset/done/$", "account.views.password_reset_done", name="acct_passwd_reset_done"),
    url(r"^password_reset_key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", "account.views.password_reset_from_key", name="acct_passwd_reset_key"),
    url(r"^fb_invite_sent/$", "account.views.fb_invite_sent", name="fb_invite_sent"),
    url(r"^fb_invite_accepted/$", "account.views.fb_invite_accepted", name="fb_invite_accepted"),
    url(r"^remove_child/(?P<child_id>\d+)/$", "account.views.remove_child", name="remove_child"),
    url(r"^deactivate_account/$", "account.views.deactivate_account", name="deactivate_account"),
#    # ajax validation
    (r"^validate/$", "ajax_validation.views.validate", {"form_class": SignupForm}, "signup_form_validate"),


)
