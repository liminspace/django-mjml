import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'test'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'mjml',
    'testprj',
)

MIDDLEWARE_CLASSES = ()

ROOT_URLCONF = 'testprj.urls'

WSGI_APPLICATION = 'testprj.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3'),
        'NAME': ':memory:',
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.template.context_processors.request',
            ),
        },
    },
]

MJML_BACKEND = 'cmd'
MJML_EXEC_CMD = os.path.join(os.path.dirname(BASE_DIR), 'node_modules', '.bin', 'mjml')
MJML_TCPSERVERS = (
    ('127.0.0.1', 28101),
    ('127.0.0.1', 28102),
    ('127.0.0.1', 28103),
)
MJML_HTTPSERVERS = (
    {
        'URL': 'http://127.0.0.1:38101/v1/render',
    },
    {
        'URL': 'http://127.0.0.1:38102/v1/render',
    },
)

DEFAULT_MJML_VERSION = 4
