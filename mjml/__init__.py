import django

__version__ = '1.5'

if django.VERSION < (3, 2):
    default_app_config = 'mjml.apps.MJMLConfig'
