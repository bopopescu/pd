from django.contrib import admin
from models import WaitingList


class WLAdmin(admin.ModelAdmin):
    list_display = ('email','zip_code','signup_date')
    search_fields = ('zip_code', 'signup_date')

# admin.site.register(WaitingList, WLAdmin)

