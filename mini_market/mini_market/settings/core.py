import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = BASE_DIR.joinpath('.env')

if dotenv_file.is_file():
    load_dotenv(dotenv_file)

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True if os.environ.get('DEBUG', 'False') == 'True' else False

ON_DEV = False if os.getenv('ON_DEV', 'True') == 'False' else True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split()

CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS').split()


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'djoser',
    'drf_spectacular',
]

PROJECT_APPS = [
    'apps.products',
    'apps.api',
]

INSTALLED_APPS += PROJECT_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mini_market.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mini_market.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

PAYMENT_URL = os.environ.get('PAYMENT_URL', 'empty')
PAYMENT_TOKEN = os.environ.get('PAYMENT_TOKEN', 'empty')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'error_logs.log',
        }
    },
    'loggers': {
        '': {
            'level': 'ERROR',
            'handlers': ['file']
        }
    }
}
