from notify.models import inbox_count_for
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

_inbox_count_sources = None



def inbox(request):
    if request.user.is_authenticated():
        return {'messages_inbox_count': inbox_count_for(request.user)}
    else:
        return {}

def inbox_count_sources():
    global _inbox_count_sources
    if _inbox_count_sources is None:
        sources = []
        for path in settings.COMBINED_INBOX_COUNT_SOURCES:
            i = path.rfind('.')
            module, attr = path[:i], path[i+1:]
            try:
                mod = __import__(module, {}, {}, [attr])
            except ImportError, e:
                raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
            sources.append(func)
        _inbox_count_sources = tuple(sources)
    return _inbox_count_sources


def combined_inbox_count(request):
    """
    A context processor that uses other context processors defined in
    setting.COMBINED_INBOX_COUNT_SOURCES to return the combined number from
    arbitrary counter sources.
    """
    count = 0
    for func in inbox_count_sources():
        counts = func(request)
        if counts:
            for value in counts.itervalues():
                try:
                    count = count + int(value)
                except (TypeError, ValueError):
                    pass
    return {
        "combined_inbox_count": count,
    }

