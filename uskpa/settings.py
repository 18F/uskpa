"""
Django settings for uskpa project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '!!NOT-A-SECRET!!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False) == "TRUE"
CI_TESTING = os.environ.get('CI_TESTING', False) == "TRUE"
IS_DEPLOYED = not DEBUG and not CI_TESTING

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'localflavor',
    'kpc.apps.KpcConfig',
    'accounts.apps.AccountsConfig',
    'django.contrib.admin',
    'simple_history',
    'django_filters'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',

]

ROOT_URLCONF = 'uskpa.urls'

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

WSGI_APPLICATION = 'uskpa.wsgi.application'

DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/2.0/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#using-argon2-with-django
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# Set admin list
admins = os.environ.get('ADMINS', '')
if admins:
    ADMINS = [('', email) for email in admins.split(',')]
else:
    ADMINS = []
MANAGERS = ADMINS

if not IS_DEPLOYED:
    AUTH_PASSWORD_VALIDATORS = []
    ALLOWED_HOSTS = ['*']
elif IS_DEPLOYED:
    # PRODUCTION SETTINGS
    # ------------------------------------------------------------------------------
    ALLOWED_HOSTS = ['.herokuapp.com']
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
    # Logout users after 20 minutes of inactivity
    SESSION_SAVE_EVERY_REQUEST = True
    SESSION_COOKIE_AGE = 20 * 60

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = os.environ.get('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', True)
    # TODO: set this to 60 seconds first and then to 518400 once you prove the former works
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', True)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# MAIL
# default to mailhog for development, let env configure SendGrid otherwise
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get(
    'DJANGO_DEFAULT_FROM_EMAIL',
    default='NOT-CONFIGURED@LOCALHOST.ORG'
)
EMAIL_SUBJECT_PREFIX = os.environ.get('DJANGO_EMAIL_SUBJECT_PREFIX', default='[LOCALHOST] ')

if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    # We're local, mailhog
    EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', 'mailhog')
    EMAIL_PORT = os.environ.get('DJANGO_EMAIL_PORT', 1025)
elif EMAIL_BACKEND.startswith("anymail"):
    INSTALLED_APPS += ['anymail']

    ANYMAIL = {
        "SENDGRID_API_KEY": os.environ.get('SENDGRID_API_KEY'),
    }
    if not ANYMAIL["SENDGRID_API_KEY"]:
        raise ImproperlyConfigured(f'SENDGRID_API_KEY must be set when EMAIL_BACKEND={EMAIL_BACKEND}')


SHOW_CERT_PDF_ADDRESS_BOUNDARY = False
KPC_BASE = os.path.join(BASE_DIR, 'kpc', 'resources', 'kpc_base.pdf')
