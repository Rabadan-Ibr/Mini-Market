import os

from .core import BASE_DIR, ON_DEV

DATABASES_MAP = {
    'production': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'db'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', 5432)
    },
    'dev': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

DATABASES = dict()
DATABASES['default'] = DATABASES_MAP['dev'] if ON_DEV else DATABASES_MAP['production']
