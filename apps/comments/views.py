from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.contenttypes.models import ContentType


from mydebug import *
import re
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
import urllib, simplejson
from datetime import datetime
from my_django_utils import PDEncoder, get_status_date_format


from models import *

def new_comment(request, **kwargs):
    if request.method == 'POST':
        post = request.POST
        model = post["model"]
        app_label = post["app_label"]
        id = post["id"]
        comment = post["comment"]
        
        email = None
        if 'email' in post:
            email=post["email"]



        if not re.match('^[0-9]+$',id):
            raise Exception('invalid object id')

        if not re.match('^[\w]+$',model):
            raise Exception('invalid model')

        if not re.match('^[\w]+$',app_label):
            raise Exception('invalid app_label')


        obj_type = ContentType.objects.get(app_label=app_label, model=model)

        item = obj_type.get_object_for_this_type(id=id)

        if not item.can_view_comments(request.user):
            raise Exception('no comments for you')
        
        if request.user.is_authenticated():        
            c = Comment(item=item, comment=comment, user=request.user)
        else:
            c = Comment(item=item, comment=comment, user_email=email)
                    
        c.save()

        record = {}

        if request.user.is_authenticated():           
            user_profile = request.user.get_profile().get_profile()
            record.update({
                               'small_profile_pic': user_profile["small_profile_pic"],
                               'first_name': user_profile["first_name"],
                               'last_name': user_profile["last_name"],
                          })
        else:        
            record.update({ 'email': c.user_email })

        record.update({
                       'comment':c.comment,
                       'when':get_status_date_format(c.added),
                       'when_full':c.added,
                     })


        response_dict = { "success":True, "message": "Done", "comment": record }

        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')
        
    
    return True



def list_comments(request, **kwargs):
    if request.method == 'POST':
        post = request.POST
        model = post["model"]
        app_label = post["app_label"]
        id = post["id"]

        if not re.match('^[0-9]+$',id):
            raise Exception('invalid object id')

        if not re.match('^[\w]+$',model):
            raise Exception('invalid model')

        if not re.match('^[\w]+$',app_label):
            raise Exception('invalid app_label')


        obj_type = ContentType.objects.get(app_label=app_label, model=model)

        item = obj_type.get_object_for_this_type(id=id)
        
        if not item.can_view_comments(request.user):
            raise Exception('no comments for you')

        comments = list(item.comments.select_related('user','user___profile_cache', 'user___profile_cache__photo', 'user___profile_cache__album').all())


        ajax_comments = []
        for comment in comments:
            record = {}
            if comment.user is not None:
                user_profile = comment.user.get_profile().get_profile()
                record.update({
                               'small_profile_pic': user_profile["small_profile_pic"],
                               'first_name': user_profile["first_name"],
                               'last_name': user_profile["last_name"],
                              })
            else:
                record.update({ 'email': comment.user_email })

            record.update({
                           'comment':comment.comment,
                           'when':get_status_date_format(comment.added),
                           'when_full':comment.added,
                           })
            
            ajax_comments.append(record)
        
        response_dict = { "success":True, "comments":ajax_comments }

        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')

    
    return True

