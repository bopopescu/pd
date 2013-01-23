from django.contrib import admin

from profiles.models import Profile, Child, FacebookUser

class ProfileAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "gender", "source", "zip_code"]

admin.site.register(Profile, ProfileAdmin)
#admin.site.register(Child)
#admin.site.register(FacebookUser)


from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'date_joined', 'is_active')
    ordering = ['-date_joined']
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
