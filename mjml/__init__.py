import django

__version__ = '1.2'

if django.VERSION < (3, 2):
    default_app_config = 'mjml.apps.MJMLConfig'
