import re

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import smart_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.http import int_to_base36

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.forms.extras.widgets import SelectDateWidget

from django.forms.formsets import formset_factory


from django.core.validators import validate_email

from pinax.core.utils import get_send_mail
send_mail = get_send_mail()

from emailconfirmation.models import EmailAddress
from timezones.forms import TimeZoneField

from account.models import Account, PasswordReset
from account.models import OtherServiceInfo, other_service, update_other_services
from account.utils import user_display, perform_login, generate_id
from schools.models import School, PD_School
from profiles.models import Profile
from profiles.models import Child
from profiles.models import Adult_Child
import datetime
#from friends.importer import import_vcards

import datetime
import re

from notify.models import send_email

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from mydebug import *
from widgets import *
from places.models import Zip



alnum_re = re.compile(r"^\w+$")


# @@@ might want to find way to prevent settings access globally here.
REQUIRED_EMAIL = getattr(settings, "ACCOUNT_REQUIRED_EMAIL", False)
EMAIL_VERIFICATION = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", False)
EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", False)


class GroupForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop("group", None)
        super(GroupForm, self).__init__(*args, **kwargs)


class LoginForm(GroupForm):
    
    password = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    remember = forms.BooleanField(
        label = _("Remember Me"),
        help_text = _("If checked you will stay logged in for 3 weeks"),
        required = False
    )
    
    user = None
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        ordering = []
        if EMAIL_AUTHENTICATION:
            self.fields["email"] = forms.EmailField(
                label = ugettext("E-mail"),
            )
            ordering.append("email")
        else:
            self.fields["username"] = forms.CharField(
                label = ugettext("Username"),
                max_length = 30,
            )
            ordering.append("username")
        ordering.extend(["password", "remember"])
        self.fields.keyOrder = ordering
    
    def user_credentials(self):
        """
        Provides the credentials required to authenticate the user for
        login.
        """
        credentials = {}
        if EMAIL_AUTHENTICATION:
            credentials["email"] = self.cleaned_data["email"]
        else:
            credentials["username"] = self.cleaned_data["username"]
        credentials["password"] = self.cleaned_data["password"]
        return credentials
    
    def clean(self):
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account has not been verified yet."))
        else:
            if EMAIL_AUTHENTICATION:
                error = _("The e-mail address and/or password you specified are not correct.")
            else:
                error = _("The username and/or password you specified are not correct.")
            raise forms.ValidationError(error)
        return self.cleaned_data
    
    def login(self, request):
        perform_login(request, self.user)
        if self.cleaned_data["remember"]:
            request.session.set_expiry(60 * 60 * 24 * 7 * 3)
        else:
            request.session.set_expiry(0)

GENDER_CHOICES = (
    ('male', 'Boy'),
    ('female', 'Girl'),
)

class ChildForm(forms.Form):
    GENDER_CHOICES = (
        ('male', 'Boy'),
        ('female', 'Girl'),
    )

    RELATION_CHOICES = (
        ('parent','Parent'),
        ('caregiver','Caregiver'),
    )
    
    first_name = forms.CharField(
        label = _("First Name:"),
        max_length = 30,
        widget = forms.TextInput()
    )
    last_name = forms.CharField(
        required = False,
        label = _("Last Name:"),
        max_length = 30,
        widget = forms.TextInput()
    )
    birthdate = forms.DateField(
        widget=CustomSelectDateWidget(years=range(2000, datetime.date.today().year+1),             
                                      attrs={'class_year':'select_short select_not_zero',
                                             'class_month':'select_long select_not_zero',
                                             'class_day':'select_short select_not_zero'}),
        label = _("Birth Date")
        
    )
    gender = forms.ChoiceField(
        widget = forms.RadioSelect(), 
        choices=GENDER_CHOICES
    )
    school = forms.CharField(
        required = False,
        label = _("School"),
        max_length = 20,
        widget = forms.TextInput()                             
    )    

    schoolname = forms.CharField(
        required = False,
        label = _("School"),
        max_length = 100,
        widget = forms.TextInput()                             
    )    

    relation = forms.ChoiceField(
        widget = forms.RadioSelect(),
        choices=RELATION_CHOICES
    )

    def __init__(self, *args, **kwargs):
        super(ChildForm, self).__init__(*args, **kwargs)

        
    def save(self, request=None):

        child = Child()
        child.first_name = self.cleaned_data["first_name"]
        child.first_name = child.first_name.title()
        child.last_name = self.cleaned_data["last_name"]
        if child.last_name is None or (len(child.last_name) == 0):
            child.last_name = request.user.get_profile().last_name

        child.gender = self.cleaned_data["gender"]
        child.birthdate = self.cleaned_data["birthdate"]
        school = self.cleaned_data["school"]
        schoolname = self.cleaned_data["schoolname"]

        sch = None
        if (len(school)):
            sch = School.objects.get(id=school)
        elif (len(schoolname)):
            pd_sch, fa = PD_School.objects.get_or_create(name=schoolname)
            sch,fa  = School.objects.get_or_create(gsid="PD"+str(pd_sch.id), name=schoolname, pd=True)

        if sch is not None:
            child.school = sch

        child.save()

        relation = self.cleaned_data["relation"]

        childrelation = Adult_Child()
        childrelation.adult=request.user
        childrelation.child=child
        childrelation.relation=settings.RELATION_TYPES_DICT[relation]
        childrelation.set_admin_perms()
        childrelation.save()
                
        return True



class SignupForm(forms.Form):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
        
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'class':'ipt clearMeFocus'}
        )
    )
    first_name = forms.CharField(
        label = _("First Name:"),
        max_length = 30,
        widget = forms.TextInput()
    )
    last_name = forms.CharField(
        label = _("Last Name:"),
        max_length = 30,
        widget = forms.TextInput()
    )
    zip_code = forms.CharField(
        label = _("Zip Code:"),
        max_length = 5,
        widget = forms.TextInput()
    )
    gender = forms.ChoiceField(
        widget = forms.RadioSelect(), 
        choices=GENDER_CHOICES
    )
    password1 = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    confirmation_key = forms.CharField(
        max_length = 40,
        required = False,
        widget = forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        if REQUIRED_EMAIL or EMAIL_VERIFICATION or EMAIL_AUTHENTICATION:
            self.fields["email"].label = ugettext("E-mail")
            self.fields["email"].required = True
        else:
            self.fields["email"].label = ugettext("E-mail (optional)")
            self.fields["email"].required = False
        
    def clean_email(self):
        value = self.cleaned_data["email"]
        if UNIQUE_EMAIL or EMAIL_AUTHENTICATION:
            try:
                User.objects.get(email__iexact=value)
            except User.DoesNotExist:
                return value
            raise forms.ValidationError(_("A user is registered with this e-mail address."))
        return value

    def clean_zip_code(self):
        value = self.cleaned_data["zip_code"]
        zc = None
        try:
            zc = Zip.objects.get(zip=value)
        except:
            raise forms.ValidationError(_("Please enter a valid zip code."))
        return zc

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data


    def create_user(self, fname, lname, email, password):
        user = User()
        email = email.strip().lower()
        user.username = generate_id(fname, lname, email)
        user.email = email
        password = password
        user.set_password(password)
        user.save()
        return user

    
    def create_profile(self, user=None, profile_data=None, commit=True):
        profile = Profile()
        if user is None:
            raise NotImplementedError("SignupForm.create_profile requires a valid user")
            
        profile.user = user
        profile.first_name = profile_data["first_name"]
        profile.last_name = profile_data["last_name"]
        profile.zip_code = profile_data["zip_code"]
        profile.gender = profile_data["gender"]
        profile.source = profile_data["source"]
        
        profile.save()
        
        return profile 



    def login(self, request, user):
        # nasty hack to get get_user to work in Django
        user.backend = "django.contrib.auth.backends.ModelBackend"
        perform_login(request, user)

    def save(self, request=None):
        # don't assume a username is available. it is a common removal if
        # site developer wants to use e-mail authentication.
        #  username = self.cleaned_data.get("username")
        
        email = self.cleaned_data["email"].strip().lower()
        password = self.cleaned_data.get("password1")

        profile_data = { 
            'first_name':  self.cleaned_data["first_name"],
            'last_name':  self.cleaned_data["last_name"],
            'zip_code': self.cleaned_data["zip_code"],
            'gender': self.cleaned_data["gender"],
            'source': request.session.get('source', settings.DEFAULT_SOURCE)
        }


        is_join_invitation = False

        if self.cleaned_data["confirmation_key"]:
            from friends.models import JoinInvitationEmail # @@@ temporary fix for issue 93
            try:
                join_invitation = JoinInvitationEmail.objects.get(confirmation_key=self.cleaned_data["confirmation_key"])
                is_join_invitation = True
            except JoinInvitationEmail.DoesNotExist:
                pass

        new_user = self.create_user(profile_data['first_name'],profile_data['last_name'],email, password)
        new_profile = None

        try:       
            new_profile = self.create_profile(new_user, profile_data)
        except:
            pass
        
        if new_profile is None:
            new_user.delete()
            raise Exception('User creation failed. Please try again later')

        else:        
            if is_join_invitation:
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email == join_invitation.contact.email:
                    EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
                    send_email(new_user.email, 'welcome_email', ctx = { 'actor':new_profile }, skip_footer=True)
            else:       
                EmailAddress.objects.add_email(new_user, email)
            
                if EMAIL_VERIFICATION:
                    new_user.is_active = False
                    new_user.save()
            
            self.after_signup(new_user)
    
            return new_user


    
    def after_signup(self, user, **kwargs):
        """
        An extension point for subclasses.
        """
        pass


class UserForm(forms.Form):
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)


class AccountForm(UserForm):
    
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        try:
            self.account = Account.objects.get(user=self.user)
        except Account.DoesNotExist:
            self.account = Account(user=self.user)


class AddEmailForm(UserForm):
    
    email = forms.EmailField(
        label = _("E-mail"),
        required = True,
        widget = forms.TextInput(attrs={"size": "30"})
    )
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        errors = {
            "this_account": _("This e-mail address already associated with this account."),
            "different_account": _("This e-mail address already associated with another account."),
        }
        if UNIQUE_EMAIL:
            try:
                email = EmailAddress.objects.get(email__iexact=value)
            except EmailAddress.DoesNotExist:
                return value
            if email.user == self.user:
                raise forms.ValidationError(errors["this_account"])
            raise forms.ValidationError(errors["different_account"])
        else:
            try:
                EmailAddress.objects.get(user=self.user, email__iexact=value)
            except EmailAddress.DoesNotExist:
                return value
            raise forms.ValidationError(errors["this_account"])
    
    def save(self):
        return EmailAddress.objects.add_email(self.user, self.cleaned_data["email"])


class ChangePasswordForm(UserForm):
    
    oldpassword = forms.CharField(
        label = _("Current Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password1 = forms.CharField(
        label = _("New Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("New Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def clean_oldpassword(self):
        if not self.user.check_password(self.cleaned_data.get("oldpassword")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["oldpassword"]
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


class SetPasswordForm(UserForm):
    
    password1 = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()


class ResetPasswordForm(forms.Form):
    
    email = forms.EmailField(
        label = _("E-mail"),
        required = True,
        widget = forms.TextInput(attrs={"size":"30"})
    )
    
    def clean_email(self):
        if EmailAddress.objects.filter(email__iexact=self.cleaned_data["email"], verified=True).count() == 0:
            raise forms.ValidationError(_("E-mail address not verified for any user account"))
        return self.cleaned_data["email"]
    
    def save(self, **kwargs):
        
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)
        
        for user in User.objects.filter(email__iexact=email):
            
            temp_key = token_generator.make_token(user)
            
            # save it to the password reset model
            password_reset = PasswordReset(user=user, temp_key=temp_key)
            password_reset.save()
            
            current_site = Site.objects.get_current()
            domain = unicode(current_site.domain)
            
            # send the password reset email
            subject = _("Password reset e-mail sent")
            message = render_to_string("account/password_reset_key_message.txt", {
                "user": user,
                "uid": int_to_base36(user.id),
                "temp_key": temp_key,
                "domain": domain,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], priority="high")
        return self.cleaned_data["email"]


class ResetPasswordKeyForm(forms.Form):
    
    password1 = forms.CharField(
        label = _("New Password"),
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = _("New Password (again)"),
        widget = forms.PasswordInput(render_value=False)
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
    
    def clean_password2(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password2"]
    
    def save(self):
        # set the new user password
        user = self.user
        user.set_password(self.cleaned_data["password1"])
        user.save()
        # mark password reset object as reset
        PasswordReset.objects.filter(temp_key=self.temp_key).update(reset=True)


class ChangeTimezoneForm(AccountForm):
    
    timezone = TimeZoneField(label=_("Timezone"), required=True)
    
    def __init__(self, *args, **kwargs):
        super(ChangeTimezoneForm, self).__init__(*args, **kwargs)
        self.initial.update({"timezone": self.account.timezone})
    
    def save(self):
        self.account.timezone = self.cleaned_data["timezone"]
        self.account.save()


class ChangeLanguageForm(AccountForm):
    
    language = forms.ChoiceField(
        label = _("Language"),
        required = True,
        choices = settings.LANGUAGES
    )
    
    def __init__(self, *args, **kwargs):
        super(ChangeLanguageForm, self).__init__(*args, **kwargs)
        self.initial.update({"language": self.account.language})
    
    def save(self):
        self.account.language = self.cleaned_data["language"]
        self.account.save()


class TwitterForm(UserForm):
    username = forms.CharField(label=_("Username"), required=True)
    password = forms.CharField(
        label = _("Password"),
        required = True,
        widget = forms.PasswordInput(render_value=False)
    )
    
    def __init__(self, *args, **kwargs):
        super(TwitterForm, self).__init__(*args, **kwargs)
        self.initial.update({"username": other_service(self.user, "twitter_user")})
    
    def save(self):
        from microblogging.utils import get_twitter_password
        update_other_services(self.user,
            twitter_user = self.cleaned_data["username"],
            twitter_password = get_twitter_password(settings.SECRET_KEY, self.cleaned_data["password"]),
        )
