from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "test"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = (
    "mjml",
    "tests",
)

MIDDLEWARE_CLASSES = ()

ROOT_URLCONF = "tests.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": ("django.template.context_processors.request",),
        },
    },
]

MJML_BACKEND_MODE = "cmd"
MJML_EXEC_CMD = BASE_DIR.parent / "node_modules/.bin/mjml"
MJML_CHECK_CMD_ON_STARTUP = False
MJML_TCPSERVERS = (
    ("127.0.0.1", 28101),
    ("127.0.0.1", 28102),
    ("127.0.0.1", 28103),
)
MJML_HTTPSERVERS = (
    {
        "URL": "http://127.0.0.1:38101/v1/render",
    },
    {
        "URL": "http://127.0.0.1:38102/v1/render",
    },
)

DEFAULT_MJML_VERSION = 4
