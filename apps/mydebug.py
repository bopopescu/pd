import sys
import re
import ctypes
from django.conf import settings
import traceback

__all__ = ["tolog", "ddumper", "todebug", "trace"]

def tolog(message):
    if settings.DEBUG:
        print >> sys.stderr, message

def ddumper():
    return True

def trace():
    traceback.print_exc(file=sys.stderr)

def todebug(message):
    f = open('/tmp/debug_log', 'a')
    print >>f, str(message)
    f.close()
    
#def ddumper(o,indent=0, seen={}):
#    if "__dict__" in dir(o):
#        if indent:
#            print 
#        new_indent = indent + 4
#        for attr_key in dir(o):
#            if re.search("^__", attr_key):
#                continue
#            try:
#                attr = getattr(o, attr_key)
#            except:
#                continue
#            if re.search("method", str(attr)):
#                pass
#            else:
#                addr = ctypes.addressof(attr)
#                if addr in seen:
#                    continue
#                else:
#                    seen[addr]=1
#                print ' '*indent + attr_key + ": " ,
#                ddumper(attr,new_indent)
#    else:
#        print str(o)
