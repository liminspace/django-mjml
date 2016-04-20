from django.conf import settings


MJML_EXEC_CMD = getattr(settings, 'MJML_EXEC_CMD', 'mjml')
