from .base import *

DEBUG = True
ENABLE_DEBUG_TOOLBAR = False
ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]

# Additional development-only apps
INSTALLED_APPS += [
    "debug_toolbar",
    'django_browser_reload',
    'django_extensions',
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]
