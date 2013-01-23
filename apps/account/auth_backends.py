from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from mydebug import *

class AuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        lookup_params = {}
        if settings.ACCOUNT_EMAIL_AUTHENTICATION:
            if "email" in credentials:
                lookup_params["email"] = credentials["email"]
            else:
                lookup_params["email"] = credentials["username"]
        else:
            lookup_params["username"] = credentials["username"]
        try:
            user = User.objects.select_related('_profile_cache','_profile_cache__photo','_profile_cache__album').get(**lookup_params)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(credentials["password"]):
                return user
    
    def has_perm(self, user, perm):
        # @@@ allow all users to add wiki pages
        wakawaka_perms = [
            "wakawaka.add_wikipage",
            "wakawaka.add_revision",
            "wakawaka.change_wikipage",
            "wakawaka.change_revision"
        ]
        if perm in wakawaka_perms:
            return True
        return super(AuthenticationBackend, self).has_perm(user, perm)


    def get_user(self, user_id):
        try:
            return User.objects.select_related('_profile_cache','_profile_cache__photo','_profile_cache__album','_profile_cache__zip_code').get(pk=user_id)
        except User.DoesNotExist:
            return None



EmailModelBackend = AuthenticationBackend