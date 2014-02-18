from custom_constants import *
import os
import os.path

ADMINS = (
    ('Mark Micchelli', 'mark.micchelli@mssm.edu'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ["DASHBOARD_NGS_SECRET_KEY"]

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pbg.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pbg.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'apps.analysis',
    'apps.core',
    'apps.runstatus',
    'apps.comments',
    'apps.uploads',
    'apps.projects',
    'apps.cancer',
    'south',
    'discover_runner',
    'registration',
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Added by MM for user-specific projects
AUTH_PROFILE_MODULE = "core.UserProfile"

# This should only be True when the run environment has access to the
# Minerva database
SHOW_RESULTS = True

# Added by MM to simplify our ugly Apache workaround. Summary: if I
# create a Django-related htaccess file in my root 'www' directory, Apache
# will try to run ALL of my webpages with Django, not just the ones in this
# Django project. As a workaround, I've located a second htaccess file at
# the directory specified by UGLY_PREFIX, which leaves my other webpages
# untouched. As a consequence, I need to manually prefix every Django URL
# with the UGLY_PREFIX, which is, well, ugly. Look at pbg/urls.py to get
# a sense of what I mean.
UGLY_PREFIX = "dashboard/"

# Relative URLs are only used in pbg.urls, and they differ only in that they
# lack a leading slash. Regular LOGIN_URL and LOGOUT_URL are used more often.
LOGIN_URL = "/" + UGLY_PREFIX + "accounts/login/"
LOGOUT_URL = "/" + UGLY_PREFIX + "accounts/logout/"

# For better test layout
TEST_RUNNER = 'discover_runner.DiscoverRunner'

# For registration
ACCOUNT_ACTIVATION_DAYS = 7

# For email sending
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'mssm.pbg@gmail.com'
EMAIL_HOST_PASSWORD = os.environ['DASHBOARD_NGS_GMAIL_PASSWORD']
