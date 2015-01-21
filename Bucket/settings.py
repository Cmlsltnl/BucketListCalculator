"""
Django settings for Bucket project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from settings_secret import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'BucketList',
    'south',
    'avatar',
    'django_messages',
    'chartit',
    'password_reset',
    'django.contrib.humanize',
    'djangosecure',
     'sendgrid',
    
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
)


TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ROOT_URLCONF = 'Bucket.urls'

WSGI_APPLICATION = 'Bucket.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = 'https://bucketlistcalculator.com/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'media/static')]

MEDIA_URL = 'https://bucketlistcalculator.com/media/'

AVATAR_GRAVATAR_BACKUP = False

AVATAR_DEFAULT_URL = 'https://bucketlistcalculator.com/static/images/default-avatar.png'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

if DEBUG:
    try : 
        from dev_settings import *
    except ImportError as e:
        pass

