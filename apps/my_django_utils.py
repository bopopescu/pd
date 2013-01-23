import simplejson


from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME

def children_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.get_profile().has_children(),
        redirect_field_name=redirect_field_name,
        login_url='/account/add_children',
    )
    if function:
        return actual_decorator(function)
    return actual_decorator



def select_related_generic_prop(list_of_items, generic_relation_name, prop):
    from django.contrib.contenttypes.models import ContentType
    generics = {}

    for item in list_of_items:
        obj = getattr(item, prop)
        generics.setdefault(obj.content_type_id, set()).add(obj.object_id)

    content_types = ContentType.objects.in_bulk(generics.keys())
    relations = {}

    for ct, fk_list in generics.items():
        ct_model = content_types[ct].model_class()
        relations[ct] = ct_model.objects.in_bulk(list(fk_list))

    cache_key_name = '_' + generic_relation_name + '_cache'

    for item in list_of_items:
        obj = getattr(item, prop)
        setattr(item, cache_key_name,
                relations[obj.content_type_id][obj.object_id])



def select_related_generic(list_of_items, generic_relation_name):
    from django.contrib.contenttypes.models import ContentType
    generics = {}

    for item in list_of_items:
        generics.setdefault(item.content_type_id, set()).add(item.object_id)

    content_types = ContentType.objects.in_bulk(generics.keys())
    relations = {}

    for ct, fk_list in generics.items():
        ct_model = content_types[ct].model_class()
        relations[ct] = ct_model.objects.in_bulk(list(fk_list))

    cache_key_name = '_' + generic_relation_name + '_cache'

    for item in list_of_items:
        setattr(item, cache_key_name,
                relations[item.content_type_id][item.object_id])


class PDEncoder(simplejson.JSONEncoder):

    def default(self, obj):
        from photos.models import *
        from schools.models import *
        if isinstance(obj, Photo):
            return obj.profile.url
        elif isinstance(obj, Album):
            return 'album'
        elif isinstance(obj, School):
            if len(obj.name) > 20:
                return obj.name[0:17] + "..."
            return obj.name      
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return str(type(obj))
        
        return simplejson.JSONEncoder.default(self, obj)

def get_plural(num, word):
   suffix = ''
   if num > 1:
     suffix = 's'

   return str(num) + ' ' + word + suffix


def get_status_date_format(when):
  from datetime import datetime, timedelta
  now = datetime.now()
  future = False
  diff = None
  if when < now:
    diff = now - when
  else:
    diff = when - now
    future = True

  HOUR = 60 * 60
  TWO_HOUR = 2 * HOUR
  EIGHT_HOUR = 4 * HOUR

  str_when = ''

  if diff.days >= 1:
    num = int(diff.days)
    str_when = get_plural(num, 'day')

  elif diff.seconds > 8 * HOUR:
    num = int(diff.seconds / HOUR)
    str_when = get_plural(num, 'hour')

  elif diff.seconds > HOUR:
    num_hours = int(diff.seconds / HOUR)
    hours_str_when = get_plural(num_hours, 'hour')

    num_minutes = ((diff.seconds - num_hours * HOUR) / 60)
    minutes_str_when = get_plural(num_minutes, 'minute')

    str_when = hours_str_when + ' ' + minutes_str_when

  elif diff.seconds < 60:
    seconds = diff.seconds
    if seconds == 0:
        seconds = 1;
    str_when = get_plural(seconds, 'second')
  else:
    num = int(diff.seconds / 60)
    str_when = get_plural(num, 'minute')

  if future:
    str_when = 'in ' + str_when
  else:
    str_when = str_when + ' ago'

  return str_when

