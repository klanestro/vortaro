# Django settings for esp project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))

try:
	from vortaro.local_settings import *
except ImportError: pass

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = "sqlite3"    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_ROOT + '/vortaro.sqlite'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8%^3v6a$xjvypw$fwzzsni#vlt!s#kzs63*kh^r_+avbsap*ju'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'vortaro.urls'

TEMPLATE_DIRS = (
    PROJECT_ROOT + "/templates"
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
	'vortaro.words',
#	'django.contrib.admin',
)


AUTHENTICATION_BACKENDS = (
    'vortaro.auth_backends.CustomUserModelBackend',
)

CUSTOM_USER_MODEL = 'words.Editor'

EMAIL_HOST = "mail.vortaro.co.cc"
EMAIL_PORT = 26
EMAIL_HOST_USER = "noreply@vortaro.co.cc"
EMAIL_HOST_PASSWORD = "crimson"


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "vortaro.words.context_processors.login"
)

LOGIN_URL = "/login"

from textwrap import wrap
class BogusSMTPConnection(object):
	"""Instead of sending emails, print them to the console."""
 
	def __init__(*args, **kwargs):
		print("Initialized bogus SMTP connection")
 
	def open(self):
		print("Open bogus SMTP connection")
 
	def close(self):
		print("Close bogus SMTP connection")
 
	def send_messages(self, messages):
		print("Sending through bogus SMTP connection:")
		for message in messages:
			print("From: %s" % message.from_email)
			print("To: %s" % ", ".join(message.to))
			print("Subject: %s" % message.subject)
			print("%s" % "\n".join(wrap(message.body)))
			print(messages)
			return len(messages)

if DEBUG:
	from django.core import mail
	mail.SMTPConnection = BogusSMTPConnection

