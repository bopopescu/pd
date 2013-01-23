from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)


from photos.models import create_image

import os
create_image(settings.DEFAULT_PROFILE_PHOTO_ID, "Placeholder", os.path.join(settings.PROJECT_ROOT, "media", "images/placeholder.jpg")) 
