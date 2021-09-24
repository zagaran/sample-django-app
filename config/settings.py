"""
Django settings.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ
from django.contrib.messages import constants as messages


env = environ.Env(
    DEBUG=(bool, False),
    DEBUG_TOOLBAR=(bool, False),
    WEBPACK_LOADER_HOTLOAD=(bool, False),
    LOCALHOST=(bool, False),
    HOST=(str, "localhost"),
    MAINTENANCE_MODE=(bool, False),
    # START_FEATURE sentry
    SENTRY_DSN=(str, None),
    # END_FEATURE sentry
    # START_FEATURE django_ses
    AWS_SES_REGION_NAME=(str, "us-east-1"),
    AWS_SES_REGION_ENDPOINT=(str, "email.us-east-1.amazonaws.com"),
    # END_FEATURE django_ses
)
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: do not run with debug turned on in production!
DEBUG = env("DEBUG")

# run with this set to False in production
LOCALHOST = env("LOCALHOST")

ALLOWED_HOSTS = [env("HOST")]
if LOCALHOST is True:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
else:
    # START_FEATURE recommended_production_settings
    # if using AWS hosting
    from ec2_metadata import ec2_metadata
    ALLOWED_HOSTS.append(ec2_metadata.private_ipv4)
    # END_FEATURE recommended_production_settings

# Application definition
THIRD_PARTY_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    # START_FEATURE django_social
    "social_django",
    # END_FEATURE django_social
    # START_FEATURE crispy_forms
    "crispy_forms",
    # END_FEATURE crispy_forms
    # START_FEATURE django_react
    "django_react_components",
    "webpack_loader",
    # END_FEATURE django_react
    # START_FEATURE debug_toolbar
    "debug_toolbar",
    # END_FEATURE debug_toolbar
]

LOCAL_APPS = [
    "common",
]

INSTALLED_APPS = THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "common.middleware.MaintenanceModeMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MAINTENANCE_MODE = env("MAINTENANCE_MODE")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {"default": env.db()}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# START_FEATURE django_ses
if LOCALHOST:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "webmaster@localhost"
else:
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME")
    AWS_SES_REGION_ENDPOINT = env("AWS_SES_REGION_ENDPOINT")
    AWS_SES_RETURN_PATH = env("DEFAULT_FROM_EMAIL")
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
# END_FEATURE django_ses

# Logging
# https://docs.djangoproject.com/en/dev/topics/logging/#django-security
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), os.path.join(BASE_DIR, "dist/static")]

AUTH_USER_MODEL = "common.User"


# START_FEATURE django_social
AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
]

LOGIN_URL = "index"
LOGIN_REDIRECT_URL = "index"

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("GOOGLE_OAUTH2_SECRET")
# END_FEATURE django_social

# START_FEATURE crispy_forms
CRISPY_TEMPLATE_PACK = "bootstrap4"
# END_FEATURE crispy_forms

# START_FEATURE bootstrap_messages
# Bootstrap styling for Django messages
MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}
# END_FEATURE bootstrap_messages


# START_FEATURE django_storages
if LOCALHOST is True:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = ""
else:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_DEFAULT_ACL = "private"
    AWS_S3_FILE_OVERWRITE = False
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
# END_FEATURE django_storages


# START_FEATURE debug_toolbar
DEBUG_TOOLBAR = DEBUG and env("DEBUG_TOOLBAR")
INTERNAL_IPS = ['127.0.0.1']
if DEBUG_TOOLBAR:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
# END_FEATURE debug_toolbar


# START_FEATURE django_react
if DEBUG:
    WEBPACK_LOADER_HOTLOAD = env('WEBPACK_LOADER_HOTLOAD')
    if WEBPACK_LOADER_HOTLOAD:
        WEBPACK_LOADER = {
            'DEFAULT': {
                'LOADER_CLASS': "config.webpack_loader.DynamicWebpackLoader"
            }
        }
# END_FEATURE django_react


# START_FEATURE sentry
SENTRY_DSN = env("SENTRY_DSN")
if LOCALHOST is False and SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
    )
# END_FEATURE sentry

# START_FEATURE recommended_production_security_settings
if LOCALHOST is False:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    USE_X_FORWARDED_HOST = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_HSTS_SECONDS = 60 * 60 * 1  # 1 hour
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_AGE = 60 * 60 * 3  # 3 hours
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True  # Only do this if you are not accessing the CSRF cookie with JS
# END_FEATURE recommended_production_security_settings
