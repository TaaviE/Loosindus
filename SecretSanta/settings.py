"""
Django settings for SecretSanta project.
"""

import os

import raven

from SecretSanta.secretsettings import SecretSettings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SecretSettings.SECRET_KEY
PASSWORD_SALT = SecretSettings.PASSWORD_SALT

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "jolod.aegrel.ee"]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "raven.contrib.django.raven_compat",

    "SecretSanta.apps.SecretSantaConfig",

    "",
]

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GITHUB_KEY = "0e4d1ccaa69e10471c04"
SOCIAL_AUTH_GITHUB_SECRET = "01d256a6a8006912a3e057e36f33b83568edc542"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin
    "django.contrib.auth.backends.ModelBackend",
)

RAVEN_CONFIG = {
    "dsn": SecretSettings.SENTRY_DSN,
    "release": raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

ROOT_URLCONF = "SecretSanta.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates/security"),
            os.path.join(BASE_DIR, "templates/security/email"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [

            ],
        },
    },
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
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "SecretSanta.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    #    "default": {
    #        "ENGINE": "django.db.backends.sqlite3",
    #        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    #    }
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "jolod",
        "USER": SecretSettings.DB_USERNAME,
        "PASSWORD": SecretSettings.DB_PASSWORD,
        "HOST": SecretSettings.DB_HOST,
        "PORT": SecretSettings.DB_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 9}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    SecretSettings.PASSWORD_HASHER,
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = "/static/"

SITE_ID = 1

DEFAULT_FROM_EMAIL = "(Jõulurakenduse info)jõulurakendus@aegrel.ee"