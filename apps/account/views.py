from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt


from django.forms.formsets import formset_factory

from emailconfirmation.models import EmailAddress, EmailConfirmation

from account.models import OtherServiceInfo
from profiles.models import FacebookUser, Profile, ChildView
from account.forms import AddEmailForm, ChangeLanguageForm, ChangePasswordForm
from account.forms import ChangeTimezoneForm, LoginForm, ResetPasswordKeyForm
from account.forms import ResetPasswordForm, SetPasswordForm, SignupForm
from account.forms import TwitterForm, ChildForm
from account.utils import user_display, perform_login, generate_id, get_default_redirect

from friends.models import JoinInvitationEmail
from django.http import HttpResponse, HttpResponseForbidden
import urllib, simplejson
import os, sys
from friends.models import ContactFB

import logging
import base64
import hmac
import hashlib
from mydebug import *
import re

from notify.models import get_message_preferences, save_message_preferences, send_email, post_to_own_facebook

def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """
    
    bridge = kwargs.pop("bridge", None)
    
    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }


def login(request, msg=None, **kwargs):
    
    form_class = kwargs.pop("form_class", LoginForm)
    template_name = kwargs.pop("template_name", "account/login.html")
    success_url = kwargs.pop("success_url", None)
    url_required = kwargs.pop("url_required", False)
    extra_context = kwargs.pop("extra_context", {})
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    
    group, bridge = group_and_bridge(kwargs)

    message = None
    if "message" in request.session:
        message = request.session["message"]
        del request.session["message"]

    if msg is not None:
        if msg == '1':
            message = "Already Registered"
    
    if extra_context is None:
        extra_context = {}
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)
    
    if request.method == "POST" and not url_required:
        form = form_class(request.POST, group=group)
        if form.is_valid():
            form.login(request)
            if len(request.user.get_profile().display_children) < 1:
                return HttpResponseRedirect(reverse("signup_add_children"))
            
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(group=group)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "message": message,
        "form": form,
        "url_required": url_required,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    })
    ctx.update(extra_context)
    
    return render_to_response(template_name, RequestContext(request, ctx))



def signup(request, confirmation_key = None, **kwargs):
    
    template_name = kwargs.pop("template_name", "account/account_signup.html")
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    success_url = kwargs.pop("success_url", None)
    ctx = {}
           
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)
    
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            request.session["new_user"] = True
            form.login(request,user)
            request.session["event"] = 'Registered using non-Facebook form'

            return HttpResponseRedirect(reverse("signup_connect_fb"))
    else:
        form = SignupForm()
        if confirmation_key is not None:
            try:
                join_invitation = JoinInvitationEmail.objects.get(confirmation_key=confirmation_key.lower())
                ctx.update( { "email": join_invitation.contact.email,"confirmation_key": join_invitation.confirmation_key })
                request.session["source"] = 'email_invite'

            except JoinInvitationEmail.DoesNotExist:
                pass
    
    ctx.update({
        "form": form,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    })

    return render_to_response(template_name, RequestContext(request, ctx))


def create_user(fname, lname, email, password):
    user = User()
    email = email.strip().lower()
    user.username = generate_id(fname, lname, email)
    user.email = email
    password = password
    user.set_password(password)
    user.save()
    return user


def create_profile(user, profile_data, commit=True):
    profile = Profile()
    if user is None:
        raise NotImplementedError("SignupForm.create_profile requires a valid user")
        
    profile.user = user
    profile.first_name = profile_data["first_name"]
    profile.last_name = profile_data["last_name"]
    profile.fb_account_linked = profile_data["fb_account_linked"]
    profile.fb_id = profile_data["fb_id"]
    profile.fb_stream_publish = profile_data["fb_stream_publish"]
    profile.source = profile_data["source"]   
    profile.gender = profile_data["gender"]
    profile.fb_login = profile_data["fb_login"]
    profile.zip_code = profile_data["zip_code"]
    
    profile.save()
    
    return profile 

def create_fbuser(user, uid, token, name = None):
    fb_user = FacebookUser()
    fb_user.user=user
    fb_user.access_token=token
    fb_user.facebook_id=uid    
    fb_user.name = name
    fb_user.queue_for_pull = True
    fb_user.save()
    return fb_user 


def determine_zip(location):
    if location is None:
        return None

    try:
        city, state = location['name'].split(',')
        city = city.strip()
        state = state.strip()
    except:
        return None

    from places.models import Zip


    try:
        zs = Zip.objects.filter(city=city, state_full=state)[:1].get()
    except Zip.DoesNotExist:
        return None

    return zs

@csrf_exempt
def connect_login(request):
    import account.graphapi as facebook

    token = uid = fb_exists = name = None

    fb_user = facebook.get_user_from_cookie(request.COOKIES, settings.FB_API_KEY, settings.FB_SECRET_KEY)

    if fb_user is None:
        return HttpResponseRedirect(reverse("nl_home"))
        
    
    token = fb_user['access_token']
    uid = fb_user['uid']

    try:
        fb_user = FacebookUser.objects.select_related('user').get(facebook_id=uid)
        if (token is not None) and (fb_user.access_token != token):
            fb_user.access_token = token
            fb_user.save()
        
        user = fb_user.user
        user.backend = "django.contrib.auth.backends.ModelBackend"
        perform_login(request, user)
        return HttpResponseRedirect(reverse("home"))

    except FacebookUser.DoesNotExist:
        pass

    fb_api = facebook.GraphAPI(fb_user['access_token'])
    data = fb_api.get_object("me")

    todebug(data)
    zs = None
    if 'location' in data:
        location = data['location']
        zs = determine_zip(location)

    profile_data = { 
        'first_name':  data.get('first_name', None),
        'last_name':  data.get('last_name', None),
        'email': data.get('email', None),
        'name': data.get('name', None),
        'gender': data.get("gender", 'female'),
        'fb_id': uid,
        'fb_stream_publish': False,
        'fb_login':True,
        'fb_account_linked': True,
        'source': request.session.get('source', settings.DEFAULT_SOURCE),
        'zip_code':zs,
    }

    try:
        check_user = User.objects.get(email=profile_data['email'])
        request.session["message"] = "Your email address is already registered. Please log in"
        return HttpResponseRedirect(reverse("acct_login"))
    except User.DoesNotExist:
        pass


    new_user = create_user(profile_data['first_name'],profile_data['last_name'], profile_data['email'], 'nrd9371933722#2')

    new_profile = None
    
    try:            
        new_profile = create_profile(new_user, profile_data)
    except:
        import sys
        todebug("Unexpected error:"+ str(sys.exc_info()[0]))
        new_user.delete()

    fb_user = create_fbuser(new_user, uid, token, name = profile_data['name'])

    new_user.backend = "django.contrib.auth.backends.ModelBackend"
    perform_login(request, new_user)

    args = {
        'link': 'http://'+settings.WWW_HOST + reverse("nl_home"),
        'attribution':'Playdation',
        'name': new_profile.first_name + "'s life just got easier.  " + new_profile.third_person + " just joined Playdation!",
        'description':"Playdation is what the other parents and I are now using to schedule our children's playdates.",
        'picture':'http://'+settings.WWW_HOST+'/static/images/pd_square.png',
    }
                    
#    post_to_own_facebook(token, 'user_joined', { 'actor': new_profile }, **args)

    send_email(new_user.email, 'welcome_email', ctx = { 'actor':new_profile }, skip_footer=True)


    if "confirmation_key" in request.session:
        ck = request.session["confirmation_key"]
        from friends.models import JoinInvitationEmail                
        try:
            join_invitation = JoinInvitationEmail.objects.get(confirmation_key=ck)
            join_invitation.accept(new_user) # should go before creation of EmailAddress below
        except JoinInvitationEmail.DoesNotExist:
            pass

    request.session["new_user"] = True
    request.session["event"] = 'Facebook Registration'

    return HttpResponseRedirect(reverse("signup_add_children"))

           
@csrf_exempt
def signup_fb(request, confirmation_key = None, **kwargs):
    if confirmation_key is not None:
        from friends.models import JoinInvitationEmail                
        try:
            join_invitation = JoinInvitationEmail.objects.get(confirmation_key=confirmation_key.lower())
            request.session["confirmation_key"] = join_invitation.confirmation_key
        except JoinInvitationEmail.DoesNotExist:
            pass

    return HttpResponseRedirect(reverse("nl_home"))

@login_required
def signup_connect_fb(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)


    ctx.update({ 'profile':request.user.get_profile() })
    ctx = RequestContext(request, ctx)
    return render_to_response("account/account_connect.html", ctx)

@login_required
def email(request, **kwargs):
    
    form_class = kwargs.pop("form_class", AddEmailForm)
    template_name = kwargs.pop("template_name", "account/email.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = form_class(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                messages.add_message(request, messages.INFO,
                    ugettext(u"Confirmation email sent to %(email)s") % {
                            "email": add_email_form.cleaned_data["email"]
                        }
                    )
                add_email_form = form_class() # @@@
        else:
            add_email_form = form_class()
            if request.POST["action"] == "send":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=request.user,
                        email=email,
                    )
                    messages.add_message(request, messages.INFO,
                        ugettext("Confirmation email sent to %(email)s") % {
                            "email": email,
                        }
                    )
                    EmailConfirmation.objects.send_confirmation(email_address)
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "remove":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=request.user,
                        email=email
                    )
                    email_address.delete()
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("Removed email address %(email)s") % {
                            "email": email,
                        }
                    )
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "primary":
                email = request.POST["email"]
                email_address = EmailAddress.objects.get(
                    user=request.user,
                    email=email,
                )
                email_address.set_as_primary()
    else:
        add_email_form = form_class()
    
    ctx = group_context(group, bridge)
    ctx.update({
        "add_email_form": add_email_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangePasswordForm)
    template_name = kwargs.pop("template_name", "account/password_change.html")
    
    group, bridge = group_and_bridge(kwargs)

    message = None
    
    if not request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd_set"))
    
    if request.method == "POST":
        password_change_form = form_class(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            message = 'Password successfully changed'
#            messages.add_message(request, messages.SUCCESS,
#                ugettext(u"Password successfully changed.")
#            )
            password_change_form = form_class(request.user)
    else:
        password_change_form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "form": password_change_form,
        "message": message,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_set(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_set.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd"))
    
    if request.method == "POST":
        password_set_form = form_class(request.user, request.POST)
        if password_set_form.is_valid():
            password_set_form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Password successfully set.")
            )
            return HttpResponseRedirect(reverse("acct_passwd"))
    else:
        password_set_form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "password_set_form": password_set_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ResetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_reset.html")
    reset_done = False
    
    ctx = {}
        
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            password_reset_form = form_class()
            reset_done = True
    else:
        password_reset_form = form_class()
    
    ctx.update({
        "password_reset_form": password_reset_form,
        "reset_done": reset_done,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset_done(request, **kwargs):
    
    template_name = kwargs.pop("template_name", "account/password_reset_done.html")
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset_from_key(request, uidb36, key, **kwargs):
    
    form_class = ResetPasswordKeyForm
    template_name = "account/password_reset_from_key.html"
    token_generator = default_token_generator
    
    ctx =  { }
    
    # pull out user
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404
    
    user = get_object_or_404(User, id=uid_int)
    reset_done = False
    
    if token_generator.check_token(user, key):
        if request.method == "POST":
            password_reset_key_form = form_class(request.POST, user=user, temp_key=key)

            if password_reset_key_form.is_valid():
                password_reset_key_form.save()
                password_reset_key_form = form_class()
                reset_done = True
        else:
            password_reset_key_form = form_class()

        ctx.update({
            "form": password_reset_key_form,
            "reset_done":reset_done,
        })

    else:
        ctx.update({
            "token_fail": True,
        })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def signup_add_address_book(request, **kwargs):
    return True


@login_required
def timezone_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangeTimezoneForm)
    template_name = kwargs.pop("template_name", "account/timezone_change.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Timezone successfully updated.")
            )
    else:
        form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def language_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangeLanguageForm)
    template_name = kwargs.pop("template_name", "account/language_change.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Language successfully updated.")
            )
            next = request.META.get("HTTP_REFERER", None)
            return HttpResponseRedirect(next)
    else:
        form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def other_services(request, **kwargs):
    
    from microblogging.utils import twitter_verify_credentials
    
    template_name = kwargs.pop("template_name", "account/other_services.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    twitter_form = TwitterForm(request.user)
    twitter_authorized = False
    if request.method == "POST":
        twitter_form = TwitterForm(request.user, request.POST)
        
        if request.POST["actionType"] == "saveTwitter":
            if twitter_form.is_valid():
                from microblogging.utils import twitter_account_raw
                twitter_account = twitter_account_raw(
                    request.POST["username"], request.POST["password"])
                twitter_authorized = twitter_verify_credentials(
                    twitter_account)
                if not twitter_authorized:
                    messages.add_message(request, messages.ERROR,
                        ugettext("Twitter authentication failed")
                    )
                else:
                    twitter_form.save()
                    messages.add_message(request, messages.SUCCESS,
                        ugettext(u"Successfully authenticated.")
                    )
    else:
        from microblogging.utils import twitter_account_for_user
        twitter_account = twitter_account_for_user(request.user)
        twitter_authorized = twitter_verify_credentials(twitter_account)
        twitter_form = TwitterForm(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "twitter_form": twitter_form,
        "twitter_authorized": twitter_authorized,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def other_services_remove(request):
    
    group, bridge = group_and_bridge(kwargs)
    
    # @@@ this is a bit coupled
    OtherServiceInfo.objects.filter(user=request.user).filter(
        Q(key="twitter_user") | Q(key="twitter_password")
    ).delete()
    
    messages.add_message(request, messages.SUCCESS,
        ugettext("Removed twitter account information successfully.")
    )
    
    return HttpResponseRedirect(reverse("acct_other_services"))

@login_required
def account_setup_fb_login(request, opts={}):
    server_name = request.META['HTTP_HOST']
    fb_login_next_url = 'http://'+ server_name + '/' + settings.FB_LOGIN_NEXT_URL
    fb_login_cancel_url = 'http://' + server_name +'/' + settings.FB_LOGIN_CANCEL_URL

    return fb_login_build(request, opts, fb_login_next_url, fb_login_cancel_url)


@login_required
def account_setup_fb_auth(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)

    fb_user = None

    try:
        fb_user = process_fb_auth(request)
    except FBID_Taken:
        request.session["message"] = "That Facebook Account is already associated with a different Playdation account"
        return HttpResponseRedirect(reverse("signup_add_children"))
        
    profile = request.user.get_profile()
    profile.fb_stream_publish = True
    profile.fb_account_linked = True
    profile.fb_id = fb_user.facebook_id
    profile.save()

    return HttpResponseRedirect(reverse("signup_add_children"))


def run_fb_import(request):
    profile = request.user.get_profile()
    fb_user = profile.get_facebook_user()
    if fb_user is None:
        raise Exception('no fb user')
    
    from account.graphapi import GraphAPI

    fql= "SELECT uid, name, first_name, last_name, pic_square FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me())"
    fb_api = GraphAPI(fb_user.access_token)
    friends = fb_api.fql(fql)

    app_user_friends = profile.run_getAppUsers_query()
    from profiles.models import FacebookUser
    friend_fb_users=FacebookUser.objects.filter(facebook_id__in=app_user_friends)
    fb_user_dict = {}
    for fuser in friend_fb_users:
        fb_user_dict[int(fuser.facebook_id)]=fuser.user

    from friends.models import ContactFB
    cn = 0    

    for f in friends:
        name = f["name"]
        id = f["uid"]
        fname = f["first_name"]
        lname = f["last_name"]

        if id in fb_user_dict:
            user = fb_user_dict[id]
        else:
            user = None

        try:
            obj = ContactFB.objects.get(owner=request.user, facebook_id = id)
            if obj.first_name != fname or obj.last_name != lname or obj.name != name:
                obj.first_name = fname
                obj.last_name = lname
                obj.name = name
                obj.save()
        except ContactFB.DoesNotExist:
            obj = ContactFB(
                owner = request.user,
                facebook_id = id,
                name = name,
                first_name=fname,
                last_name=lname,
                user = user
            ).save()
            cn = cn + 1

    return cn


def add_children(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)

    signup = kwargs["signup"]

    child_formset = formset_factory(ChildForm)    
    formset = child_formset(prefix="child")
    
    if request.method == "POST":
        formset = child_formset(request.POST, request.FILES, prefix="child")

        if formset.is_valid():
            forms_valid = True
            for form in formset.forms:
                if not form.is_valid():
                    forms_valid=False

            if forms_valid:                 
                for form in formset.forms:
                    form.save(request)
    
                if signup:
                    request.session["event"] = 'Added Child During Registration'
                    return HttpResponseRedirect(reverse("new_home"))
                else:
                    request.session["event"] = 'Added Child After Registration'
                    return HttpResponseRedirect(reverse("home"))

    fb_profile = None
    if signup:
        fb_user = request.user.get_profile().get_facebook_user()
        if fb_user is not None:
            from account.graphapi import GraphAPI
            fb_api = GraphAPI(fb_user.access_token)
            fb_profile = fb_api.get_object("me")

        else:
            tolog("NO FBUSER")



    ctx.update({
        "profile": request.user.get_profile(),
        "fb_profile": fb_profile,
        "child_formset": formset,
        "signup": signup,
        "message": request.session.pop("message", None),
    })

    if signup:
        return render_to_response("account/signup_add_children.html", RequestContext(request, ctx) )
    else:
        return render_to_response("account/add_children.html", RequestContext(request, ctx) )



@login_required
def signup_connect_addr_friends(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    my_profile = request.user.get_profile()
    my_children = my_profile.manage_playlist_children

    playdation_friend_users = my_profile.get_playdation_contact_friend_users()

    ctx.update({ "my_profile":my_profile,  "playdation_friends": playdation_friend_users, "my_children": my_children })

    return render_to_response("account/signup_connect_friends_addr.html", RequestContext(request, ctx) )


@login_required
def signup_connect_friends(request, **kwargs):
    return True


@login_required
def signup_email_inviter(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)

    non_user_contacts = request.user.get_profile().get_playdation_contact_non_users()

    
    ctx.update({ 'non_user_contacts': non_user_contacts })
    
    return render_to_response("account/signup_email_inviter.html", RequestContext(request, ctx) )


@login_required
def signup_fb_inviter(request, **kwargs):
    return True


@login_required
def fb_invite_sent(request, **kwargs):
    if not "ids[]" in request.GET:
        return HttpResponseRedirect(reverse("home"))

    invites = request.GET.getlist("ids[]")

    for invite_id in invites:
        if not re.match('^[0-9]+$',invite_id):
            raise Exception('Invalid input')

        try:
            invite = ContactFB.objects.get(owner = request.user, facebook_id=int(invite_id))
            invite.send_invite()
        except ContactFB.DoesNotExist:
            pass
        

    request.session["event"] = "Invited Friends from Facebook"
    
    return HttpResponseRedirect(reverse("home"))



def fb_invite_accepted(request, **kwargs):
    if not "invited_by" in request.GET:
        raise Exception("No ids passed")
    
    get = request.GET
    post = request.POST
    
    from mydebug import *

    request.session["source"] = 'fb_invite'
    
    return HttpResponseRedirect(reverse("signup_fb"))



@login_required
def fb_login_build(request, opts, next_url, cancel_url, perms = settings.FB_LOGIN_PERMS):

    query_string = {
        "return_session"  : 1,
        "session_version" : 3,
        "v"               : '1.0'
    }
    
    # load default config
    query_string.update({
        "api_key"    : settings.FB_API_KEY,
        "cancel_url" : cancel_url,
        "next"       : next_url,
        "req_perms"  : perms,
    })

    query_string.update(opts)
    
    url = "https://www.facebook.com/login.php?%s" % urllib.urlencode(query_string)    

    return HttpResponseRedirect(url)


class FBID_Taken(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

@login_required
def process_fb_auth(request):

    token = uid = fb_exists = name = None

    if request.session.has_key("fb_user"):
        if request.session["fb_user"].has_key("access_token"):
            token = str(request.session["fb_user"]["access_token"])
            uid = str(request.session["fb_user"]["uid"])

    if request.GET.has_key("session"):
        fb_user = simplejson.loads(request.GET["session"])
        request.session["fb_user"] = fb_user
        token = str(request.session["fb_user"]["access_token"])
        uid = str(request.session["fb_user"]["uid"])
        
#        name = str(request.session["fb_user"]["name"])
           
    fb_id_taken = None
    try:
        fb_id_taken = FacebookUser.objects.get(facebook_id = uid)
    except FacebookUser.DoesNotExist:
        pass

    if fb_id_taken is not None:
        if fb_id_taken.user == request.user:
            fb_exists = fb_id_taken
        else:
            raise FBID_Taken('Facebook ID already assigned')
    
    try:
        if fb_exists is None:
            fb_exists = FacebookUser.objects.get(user=request.user)
        if (token is not None) and (fb_exists.access_token != token):
            fb_exists.access_token = token
            fb_exists.facebook_id = uid
            fb_exists.save()        

        return fb_exists
    except FacebookUser.DoesNotExist:      
        fb_exists = False

    if (not fb_exists):
        from account.graphapi import GraphAPI
        fb_api = GraphAPI(token)
        prof = fb_api.get_object("me")

        fb_name = prof["name"]
        fb_user = create_fbuser(request.user, uid, token, name=fb_name)
        return fb_user

@login_required
def fb_logout(request):
    return True       


@login_required
def signup_add_address_book(request, template_name="account/signup_add_address_book.html"):
    from django.contrib.sites.models import Site
    
    return render_to_response(template_name, {
        "domain_name": Site.objects.get_current(),
    }, context_instance=RequestContext(request))


@login_required
def settings_access(request, ctx = {}):
    return render_to_response("account/settings_access.html", RequestContext(request, ctx))

@login_required
def settings_communication(request, ctx = {}):

    settings = get_message_preferences(request.user)

    changed = False
    if request.method == 'POST':
        for type in settings.keys():
            if type in request.POST:
                if settings[type] == False:
                    settings[type] = True
                    changed = True
            else:
                if settings[type] == True:
                    settings[type] = False
                    changed = True
                 
        if changed:
            save_message_preferences(request.user, settings)

        return HttpResponseRedirect(reverse("settings_communication"))

    ctx = { 'settings':settings, 'cat_settings':True }
    
    return render_to_response("account/settings_communication.html", RequestContext(request, ctx))



@login_required
def settings_privacy(request, ctx = {}):
    profile = request.user.get_profile()

    children = profile.admin_children

    if request.method == 'POST':
        basic_prof_privacy = request.POST['basic_prof_privacy']
        ext_prof_privacy = request.POST['ext_prof_privacy']
        playlist_privacy = request.POST['playlist_privacy']
        photo_privacy = request.POST['photo_privacy']
        if 'school_display' in request.POST:
            profile.school_display = True
        else:
            profile.school_display = False

        profile.save()

        for ac in children:
            child = ac.child
            child.basic_prof_privacy = basic_prof_privacy
            child.ext_prof_privacy = ext_prof_privacy
            child.playlist_privacy = playlist_privacy
            child.photo_privacy = photo_privacy
            child.save()



    ctx["child"] = children[0].child
    ctx["school_display"] = profile.school_display
    ctx['cat_settings'] = True

    return render_to_response("account/settings_privacy.html", RequestContext(request, ctx))


@login_required
def settings_account(request, ctx = {}):
    account = contact = facebook = {}
    
    profile = request.user.get_profile()

    account["email"] = request.user.email
    
    contact["phone"] = profile.phone
    
    fb_user = request.user.get_profile().get_facebook_user()

    if fb_user is not None:
        if fb_user.name is not None:
            facebook["name"] = fb_user.name

    else:
        facebook = None

    ctx["account_details"] = account
    ctx["contact"] = contact
    ctx["facebook"] = facebook
    ctx["profile"] = profile
        
    ctx['cat_settings'] = True

    ctx['children'] = profile.admin_children 

    ctx['message'] = request.session.pop("message", None)

    
    return render_to_response("account/settings_account.html", RequestContext(request, ctx))


@login_required
def fb_disconnect(request, ctx = {}):
    fb_user = request.user.get_profile().get_facebook_user()
  
    for contact in ContactFB.objects.filter(owner=request.user).all():
        contact.delete()

    if fb_user is not None:
        fb_user.delete()

    profile = request.user.get_profile()
    
    profile.fb_id = None
    profile.fb_account_linked = False
    profile.fb_stream_publish = False
    profile.save()

    return HttpResponseRedirect(reverse("settings_account"))


def beta(request, msg=None, **kwargs):
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    success_url = get_default_redirect(request, redirect_field_name)

    if request.method == "POST" and "beta" in request.POST:
        beta_code = request.POST["beta"]
        if beta_code == 'play':
            request.session["beta_ok"]=1
            return HttpResponseRedirect(success_url)
    
    ctx = {
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    }
    
    return render_to_response("account/beta.html", RequestContext(request, ctx))


@login_required
def generic_fb_login(request, arg_id = None, arg_name = None, opts={}, **kwargs):
    next_handler_name = kwargs.pop("next_handler", "home")
    cancel_handler_name = kwargs.pop("cancel_handler", "home")
    perms = kwargs.pop("perms", None)
    next_handler = cancel_handler = None

    if arg_id is not None:
        next_handler = reverse(next_handler_name, kwargs= { 'arg_name':arg_name, 'arg_id': arg_id })
        cancel_handler = reverse(cancel_handler_name, kwargs= { arg_name: arg_id })
    else:
        next_handler = reverse(next_handler_name)
        cancel_handler = reverse(cancel_handler_name)
        

    server_name = request.META['HTTP_HOST']
    fb_login_next_url = 'http://' + server_name +'/' + next_handler
    fb_login_cancel_url = 'http://'+ server_name + '/' + cancel_handler

    return fb_login_build(request, opts, fb_login_next_url, fb_login_cancel_url, perms = perms)


@login_required
def generic_fb_auth(request, arg_id = None, arg_name = None, **kwargs):
    next_handler_name = kwargs.pop("next_handler", "home")
    next_handler = None
    if arg_id is not None:
        next_handler = reverse(next_handler_name, kwargs = { arg_name: arg_id })
    else:
        next_handler = reverse(next_handler_name)

    fb_user = None
    try:
        fb_user = process_fb_auth(request)
    except FBID_Taken:
        request.session["message"] = "That Facebook Account is already associated with a different Playdation account"

        return HttpResponseRedirect(next_handler)


    if fb_user is not None:
        run_fb_import(request)
        profile = request.user.get_profile()
        profile.fb_stream_publish = True
        profile.fb_account_linked = True
        profile.fb_id = fb_user.facebook_id
        profile.save()

    return HttpResponseRedirect(next_handler)

def delete_child(child):
    from photos.models import Photo
    from profiles.models import Child, Friendship, Adult_Child, ChildView

    child.first_name='Deleted'
    child.last_name='User'
    child.about=''
    child.photo = Photo.objects.get(id=settings.DEFAULT_PROFILE_PHOTO_ID)
    child.album=None
    child.school=None
    child.summer_camp=None
    child.anon_prof_privacy='private'
    child.basic_prof_privacy='private'
    child.ext_prof_privacy='private'
    child.playlist_privacy='private'
    child.ext_prof_privacy='private'
    child.playlist_privacy='private'
    child.schedule_privacy='private'
    child.template=None
    child.playdate_requirements=None
    child.diet=None
    child.foods=None
    child.shows=None
    child.toys=None
    child.languages=None
    child.sports=None
    child.activities=None
    child.places=None
    child.teacher=None
    child.grade_level=None
    child.default_invite=None
    child.default_invite_set=False
    child.save()

    Friendship.objects.filter(Q(from_child = child) | Q(to_child = child)).delete()

    from friends.models import FriendshipInvitation, FriendSuggestion
    fi = FriendshipInvitation.objects.filter(Q(from_child = child) | Q(to_child = child)).all()
    ids = []
    for f in fi:
        ids.append(f.id)
        f.delete()

    if len(ids) > 0:
        from notify.models import InternalMessage
        InternalMessage.objects.filter(associated_item__in=ids).delete()
    
    Adult_Child.objects.filter(child = child).delete()
    FriendSuggestion.objects.filter(Q(child=child) | Q(suggested_child=child)).delete()

    from schedule.models import EventPlan
    EventPlan.objects.filter(child=child).delete()

    from playdates.models import PlaydateInviteFB, PlaydateInviteUser, PlaydateInviteEmail, Playdate

    PlaydateInviteFB.objects.filter(organizer_child=child).delete()
    PlaydateInviteEmail.objects.filter(organizer_child=child).delete()
    PlaydateInviteUser.objects.filter(organizer_child=child).delete()
    PlaydateInviteUser.objects.filter(to_child=child).delete()

    for album in child.albums.all():
        album.delete()

    return True

@login_required
def remove_child(request, child_id, standalone=False):
    if not re.match('^[0-9]+$',child_id):
        raise Exception('Invalid input')

    from profiles.models import Child, Friendship, Adult_Child, ChildView

    child = Child.objects.get(id=child_id)
    cv = ChildView(user=request.user, child=child)
    if not cv.can_admin_child:
        raise Exception("You do not have permissions for this")

    retval = delete_child(child)

    if standalone:
        return retval
    
    return HttpResponseRedirect(reverse("settings_account"))


def remove_account(user):
    from profiles.models import Child, Friendship, Adult_Child
    from photos.models import Photo

    
    profile=user.get_profile()
    profile.first_name='Deleted'
    profile.last_name='User'
    profile.zip_code=None
    profile.about=''
    profile.birthdate = None
    profile.phone=''
    profile.school_display=False

    profile.photo=Photo.objects.get(id=settings.DEFAULT_PROFILE_PHOTO_ID)
    temp_album = profile.album
    profile.album=None
    profile.fb_id=''
    profile.fb_account_linked=False
    profile.fb_stream_publish=False
    profile.save()

    if temp_album is not None:
        temp_album.delete()

    for ac in profile.admin_children:
        delete_child(ac.child)

    from places.models import Place
    Place.objects.filter(owner=user).delete()        

    from friends.models import ContactEmail, ContactFB, JoinInvitationEmail, FriendshipInvitation
    ContactEmail.objects.filter(owner=user).delete()
    ContactFB.objects.filter(owner=user).delete()
    JoinInvitationEmail.objects.filter(from_user=user).delete()

    from profiles.models import Adult_Child, Friendship, FacebookUser
    FacebookUser.objects.filter(user=user).delete()
    Adult_Child.objects.filter(adult=user).delete()
    Friendship.objects.filter(Q(from_user = user) | Q(to_user = user)).delete()

    from emailconfirmation.models import EmailAddress, EmailConfirmation
    eqs = EmailAddress.objects.filter(user=user)
    for e in eqs.all():
        EmailConfirmation.objects.filter(email_address = e).delete()
        e.delete()

    from account.models import Account, OtherServiceInfo, PasswordReset
    Account.objects.filter(user=user).delete()
    OtherServiceInfo.objects.filter(user=user).delete()
    PasswordReset.objects.filter(user=user).delete()

    fi = FriendshipInvitation.objects.filter(Q(from_user = user) | Q(to_user = user)).all()
    ids = []
    for f in fi:
        ids.append(f.id)
        f.delete()

    if len(ids) > 0:
        from notify.models import InternalMessage
        InternalMessage.objects.filter(associated_item__in=ids).delete()

    from notify.models import MessagePreference, Update
    MessagePreference.objects.filter(user=user).delete()
    Update.objects.filter(owner=user).delete()


    from playdates.models import Playdate, PlaydateInviteUser
    pi = Playdate.objects.filter(organizer=user)

    ids = []
    for f in pi:
        ids.append(f.id)
        f.delete()

    if len(ids) > 0:
        from notify.models import InternalMessage
        InternalMessage.objects.filter(associated_item__in=ids).delete()

    PlaydateInviteUser.objects.filter(to_user=user).delete()

    profile.delete()

    import hashlib

    user.email=hashlib.md5(user.email).hexdigest() + '@playdation.net';
    user.save()
    try:
        user.delete()
    except:
        pass

    return True

@login_required
def deactivate_account(request):

   
    user=request.user
    
    retval = remove_account(user)
    
    return HttpResponseRedirect(reverse("acct_logout"))



    
