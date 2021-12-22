# Custom settings for production environment

from .base import *
import os
from dotenv import load_dotenv

load_dotenv()


DEBUG = False


ADMIN_NAME = os.getenv('ADMIN_NAME')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMINS = (
    (ADMIN_NAME, ADMIN_EMAIL),
)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')



DATABASES_NAME = os.getenv('DATABASES_NAME')
DATABASES_USER = os.getenv('DATABASES_USER')
DATABASES_PASSWORD = os.getenv('DATABASES_PASSWORD')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASES_NAME,
        'USER': DATABASES_USER,
        'PASSWORD': DATABASES_PASSWORD,
    }
}