from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from .tools import mjml_render


def check_mjml_command():
    try:
        html = mjml_render('<mj-body></mj-body>').decode('utf8')
    except RuntimeError as e:
        raise ImproperlyConfigured(e)
    if '<html ' not in html:
        raise ImproperlyConfigured(
            'mjml command returns wrong result.\n'
            'Check installation mjml. See https://github.com/mjmlio/mjml#installation'
        )


class MJMLConfig(AppConfig):
    name = 'mjml'
    verbose_name = 'Use MJML in Django templates'

    def ready(self):
        check_mjml_command()
