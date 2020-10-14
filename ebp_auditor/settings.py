"""
Django settings for ebp_auditor project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.contrib.messages import constants as messages
from pathlib import Path



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6-vh)6+ohk#jqj%j%k5-g49z%p5qkpxd*(#j9+oes3ga6avbua'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if not DEBUG:
    EMAIL_BAKCEND='django.core.mail.backends.smtp.email_backend'
    EMAIL_HOST_USER='username'
    EMAIL_HOST='smtp.domain.com'
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_PASSWORD='password'
else:
    EMAIL_BACKEND=('django.core.mail.backends.console.EmailBackend')




ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',


    'crispy_forms',
    'django.contrib.humanize',
    'widget_tweaks',
    'main.templatetags.errors_extra',
    'rest_framework',
    'datatableview',
    'allauth', # new
    'allauth.account', # new

    'main.apps.MainConfig',
    'accounts.apps.AccountsConfig',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend', # new

)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

ROOT_URLCONF = 'ebp_auditor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates'))],
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

WSGI_APPLICATION = 'ebp_auditor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':'ebp_auditor',
        'USER':'postgres',
        'PASSWORD':'englert187',
        'HOST':'127.0.0.1',
        'PORT':5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR=True

THOUSAND_SEPARATOR=','


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE_DIR.joinpath('static'))] # new
STATIC_ROOT = str(BASE_DIR.joinpath('staticfiles')) # new
STATICFILES_FINDERS = [ # new
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]





MEDIA_ROOT=str(BASE_DIR.joinpath('media'))
MEDIA_URL='/media/'

AUTH_USER_MODEL="accounts.CustomUser"

LOGIN_REDIRECT_URL="client_dashboard"
ACCOUNT_LOGOUT_REDIRECT = "login"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # new
ACCOUNT_SESSION_REMEMBER = True # new
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True # new
ACCOUNT_AUTHENTICATION_METHOD = 'email' # new
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False # new
ACCOUNT_EMAIL_REQUIRED = True # new


ACCOUNT_FORMS = {
    'login': 'accounts.forms.MyCustomLoginForm',
    'signup': 'accounts.forms.MyCustomSignUpForm',
    'add_email': 'allauth.account.forms.AddEmailForm',
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'set_password': 'allauth.account.forms.SetPasswordForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
}

MESSAGE_TAGS ={
    messages.ERROR:'danger'
}
