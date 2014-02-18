from .base import *
import os

os.environ.setdefault('LANG', 'en_US')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'PBG_devngs',
        'USER': 'PBG_devngs_root',
        'PASSWORD': os.environ['DASHBOARD_NGS_DEV_DATABASE_PASSWORD'],
        'HOST': 'db.mgmt.hpc.mssm.edu',
        'PORT': '',
    }
}

UGLY_PREFIX = "staging/"
LOGIN_URL = "/" + UGLY_PREFIX + "accounts/login/"
LOGOUT_URL = "/" + UGLY_PREFIX + "accounts/logout/"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MEDIA_URL = UGLY_PREFIX + 'media/'
MEDIA_ROOT = os.path.join(os.environ["HOME"], 'www/media/dashboardngs_staging')

STATIC_URL = '/static/dashboardngs_staging/'
STATIC_ROOT = os.path.join(os.environ["HOME"], 'www/static/dashboardngs_staging')

STATICFILES_DIRS = (
    os.path.join(os.environ["HOME"], '.virtualenvs/dashboardngs/lib/python2.6/site-packages/django/contrib/admin/static/'),
    os.path.join(os.environ["HOME"], 'www/staging/dashboardngs/pbg/static/'),
)

TEMPLATE_DIRS = (
    os.path.join(os.environ["HOME"], "www/staging/dashboardngs/pbg/templates/"),
)

TEST_DIRECTORY = os.path.join(os.environ["HOME"], "www/staging/dashboardngs/dashboardngstests")

TEST_DISCOVER_TOP_LEVEL = os.path.join(os.environ["HOME"], "www/staging/dashboardngs/pbg/")
