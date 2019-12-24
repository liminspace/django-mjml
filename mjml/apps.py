from __future__ import absolute_import
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from mjml.tools import mjml_render
from mjml import settings as mjml_settings


def check_mjml_command():
    try:
        html = mjml_render('<mjml><mj-body><mj-container><mj-text>MJMLv3'
                           '</mj-text></mj-container></mj-body></mjml>')
    except RuntimeError:
        try:
            html = mjml_render('<mjml><mj-body><mj-section><mj-column><mj-text>MJMLv4'
                               '</mj-text></mj-column></mj-section></mj-body></mjml>')
        except RuntimeError as e:
            raise ImproperlyConfigured(e)
    if '<html ' not in html:
        raise ImproperlyConfigured(
            'mjml command returns wrong result.\n'
            'Check MJML is installed correctly. See https://github.com/mjmlio/mjml#installation'
        )


class MJMLConfig(AppConfig):
    name = 'mjml'
    verbose_name = 'Use MJML in Django templates'

    def ready(self):
        if mjml_settings.MJML_BACKEND_MODE == 'cmd' and mjml_settings.MJML_CHECK_CMD_ON_STARTUP:
            check_mjml_command()
