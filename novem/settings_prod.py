from . import settings

DEBUG = False

SECRET_KEY = settings.os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings.os.environ['POSTGRES_NAME'],
        'USER': settings.os.environ['POSTGRES_USER'],
        'PASSWORD': settings.os.environ['POSTGRES_PASSWORD'],
        'HOST': settings.os.environ['POSTGRES_HOST'],
        'PORT': 5432,
    }
}