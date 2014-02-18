from .base import *

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'PBG_prodngs',
        'USER': 'PBG_prodngs_root',
        'PASSWORD': os.environ['DASHBOARD_NGS_DATABASE_PASSWORD'],
        'HOST': 'db.mgmt.hpc.mssm.edu',
        'PORT': '',
    }
}

MEDIA_URL = UGLY_PREFIX + 'media/'
MEDIA_ROOT = '/hpc/users/micchm01/www/media/production'

STATIC_URL = '/static/production/'
STATIC_ROOT = '/hpc/users/micchm01/www/static/production'

STATICFILES_DIRS = (
    '/hpc/users/micchm01/.virtualenvs/dashboardngs/lib/python2.6/site-packages/django/contrib/admin/static/',
    '/projects/PBG/dashboardngs/pbg/static',
)

TEMPLATE_DIRS = (
    '/projects/PBG/dashboardngs/pbg/templates/',
)

TEST_DIRECTORY = '/projects/PBG/dashboardngs/dashboardngstests/'
