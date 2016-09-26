""" Local chapter-specific settings. """

SITE_INFO = (1, <%= http_hostname.inspect %>, <%= "#{DISPLAY.fetch('institution')} #{DISPLAY.fetch('group-name')} Site".inspect %>)
ADMINS = (
    ("LU Web group","serverlog@learningu.org"),
)
CACHE_PREFIX = "<%= slug %>"

DEFAULT_EMAIL_ADDRESSES = {
    "archive": "learninguarchive@gmail.com",
    "bounces": "learningubounces@gmail.com",
    "support": <%= DISPLAY.fetch('email').inspect %>,
    "membership": <%= DISPLAY.fetch('email').inspect %>,
    "default": <%= DISPLAY.fetch('email').inspect %>,
}

ORGANIZATION_SHORT_NAME = <%= DISPLAY.fetch('groupname').inspect %>
INSTITUTION_NAME = <%= DISPLAY.fetch('institution').inspect %>
EMAIL_HOST = " !!! TODO: FIXME !!! "
EMAIL_HOST_SENDER = EMAIL_HOST

USE_MAILMAN = False
TIME_ZONE = <%= DISPLAY.fetch('timezone').inspect %>

# File Locations
PROJECT_ROOT = <%= "#{REPO}/esp/".inspect %>

# Debug settings
DEBUG = False
SHOW_TEMPLATE_ERRORS = DEBUG
DEBUG_TOOLBAR = True # set to False to globally disable the debug toolbar

# Database
DEFAULT_CACHE_TIMEOUT = 120
DATABASE_ENGINE = "django.db.backends.postgresql_psycopg2"
DATABASE_NAME = " !!! TODO: FIXME !!! "
DATABASE_HOST = " !!! TODO: FIXME !!! "
DATABASE_PORT = " !!! TODO: FIXME !!! "

from database_settings import *

MIDDLEWARE_LOCAL = []

SECRET_KEY = " !!! TODO: FIXME !!! "
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
ALLOWED_HOSTS = [<%= http_hostname.inspect %>]

# !!! TODO: FIXME !!!
# FIGURE OUT WHERE PER-SITE CUSTOMIZATIONS GO
