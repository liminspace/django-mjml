from django.conf import settings


MJML_EXEC_CMD = getattr(settings, 'MJML_EXEC_CMD', '/usr/bin/mjml')
MJML_CACHE_KEY_PREFIX = 'mjml:tpl:'
