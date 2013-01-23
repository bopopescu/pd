from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from mydebug import *
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext
from django import forms

from django.contrib.auth.models import User
import re
from django.db.models import Q


SEARCH_TYPES = (
    ("people","User Search"),
)

class SearchForm(forms.Form):
    search_string = forms.CharField(label=_("Search For:"), max_length = 50)
#    search_type = forms.ChoiceField( label=_("Search Type"), choices = SEARCH_TYPES, required = False )

@login_required
def search(request, **kwargs):
    results = None
#    search_form = SearchForm()
    search_string = None
    if request.method == "POST":
        search_form = SearchForm(request.POST)        
        if search_form.is_valid():
            search_string = search_form.cleaned_data["search_string"]
            results = User.objects.select_related('_profile_cache').filter(Q(is_active=True) & (Q(_profile_cache__first_name__istartswith=search_string) | Q(_profile_cache__last_name__istartswith=search_string)))[:10]

    ctx = { 
           'results': results,
           'search_string': search_string,
#           'form':search_form,
    }

    template = 'search/search.html'
    return render_to_response(template, RequestContext(request, ctx))

