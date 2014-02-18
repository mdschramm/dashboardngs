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

MEDIA_ROOT = "/Users/markschramm/test-repository"
MEDIA_URL = UGLY_PREFIX + 'media/'
STATIC_URL = "/static/"

STATICFILES_DIRS = (
    '/Users/markschramm/dashboardngs/pbg/static/',
)

TEMPLATE_DIRS = (
    "/Users/markschramm/dashboardngs/pbg/templates/",
)

SHOW_RESULTS = False
