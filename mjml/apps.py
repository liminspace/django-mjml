from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from mjml import settings as mjml_settings
from mjml.tools import mjml_render


def check_mjml_command() -> None:
    try:
        html = mjml_render(
            '<mjml><mj-body><mj-container><mj-text>'
            'MJMLv3'
            '</mj-text></mj-container></mj-body></mjml>'
        )
    except RuntimeError:
        try:
            html = mjml_render(
                '<mjml><mj-body><mj-section><mj-column><mj-text>'
                'MJMLv4'
                '</mj-text></mj-column></mj-section></mj-body></mjml>'
            )
        except RuntimeError as e:
            raise ImproperlyConfigured(e) from e
    if '<html ' not in html:
        raise ImproperlyConfigured(
            'mjml command returns wrong result.\n'
            'Check MJML is installed correctly. See https://github.com/mjmlio/mjml#installation'
        )


class MJMLConfig(AppConfig):
    name = 'mjml'
    verbose_name = 'Use MJML in Django templates'

    def ready(self) -> None:
        if mjml_settings.MJML_BACKEND_MODE == 'cmd' and mjml_settings.MJML_CHECK_CMD_ON_STARTUP:
            check_mjml_command()
