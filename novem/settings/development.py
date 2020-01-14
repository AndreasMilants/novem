from . import common_settings
import os

DEBUG = True

SECRET_KEY = '54d33vo75$9%&n=9#hv$x!+(#+d5wc$o_46zbixv)z_5t07x9g'

ALLOWED_HOSTS = []

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(common_settings.BASE_DIR, '../../db.sqlite3'),
    }
}
