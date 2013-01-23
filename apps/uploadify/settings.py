from django.conf import settings
# MEDIA_URL = getattr(settings, 'MEDIA_URL', '')
MEDIA_URL = '/site_media/'



# Uploadify root folder path, relative to MEDIA_ROOT
UPLOADIFY_PATH = '%s%s' % (MEDIA_URL, '/static/js/uploadify/')

# Upload path that files are sent to
#UPLOADIFY_UPLOAD_PATH = '%s%s' % (MEDIA_URL, '/media/photos/')
UPLOADIFY_UPLOAD_PATH = '/var/www/playdation.net/playdation/site_media/media/photos'
