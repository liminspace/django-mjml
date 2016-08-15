from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from .tools import mjml_render
from . import settings as mjml_settings


def check_mjml_command():
    test_mjml = '<mjml><mj-body><mj-container></mj-container></mj-body></mjml>'
    test_result_fragment = '<html '
    try:
        html = mjml_render(test_mjml).decode('utf8')
    except RuntimeError as e:
        raise ImproperlyConfigured(e)
    if test_result_fragment not in html:
        raise ImproperlyConfigured(
            'mjml command returns wrong result.\n'
            'Check installation mjml. See https://github.com/mjmlio/mjml#installation'
        )


class MJMLConfig(AppConfig):
    name = 'mjml'
    verbose_name = 'Use MJML in Django templates'

    def ready(self):
        if mjml_settings.MJML_BACKEND_MODE == 'cmd':
            check_mjml_command()
