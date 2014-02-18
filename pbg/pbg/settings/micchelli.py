from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pbg',
        'USER': 'pbg',
        'PASSWORD': 'pbg',
        'HOST': '',
        'PORT': '',
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/Users/Micchelli/Documents/work/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = UGLY_PREFIX + 'media/'

STATIC_URL = "/static/"

STATIC_ROOT = '/Users/Micchelli/Documents/work/static/'

STATICFILES_DIRS = (
    '/Users/Micchelli/Documents/work/repos/dashboardngs/pbg/static/',
)


TEMPLATE_DIRS = (
    '/Users/Micchelli/Documents/work/repos/dashboardngs/pbg/templates/',
)

SHOW_RESULTS = False

TEST_DIRECTORY = "/Users/Micchelli/Documents/work/repos/dashboardngs/test_data"

TEST_DISCOVER_TOP_LEVEL = "/Users/Micchelli/Documents/work/repos/dashboardngs/pbg/"
