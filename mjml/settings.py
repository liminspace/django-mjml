from django.conf import settings


MJML_EXEC_PATH = getattr(settings, 'MJML_EXECUTABLE_PATH', '/usr/bin/mjml')
