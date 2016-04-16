import subprocess
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from .tools import get_mjml_popen_args


def check_mjml_command():
    args = get_mjml_popen_args()
    try:
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        r = p.communicate('<mj-body></mj-body>')[0]
    except (IOError, OSError), e:
        raise ImproperlyConfigured(
            'Problem to run command "{}"\n'.format(' '.join(args)) +
            '{}\n'.format(e) +
            'Check that mjml is installed. See https://github.com/mjmlio/mjml#installation'
        )
    if '<html ' not in r:
        raise ImproperlyConfigured(
            'mjml command returns wrong result.\n'
            'Check installation mjml. See https://github.com/mjmlio/mjml#installation'
        )


class MJMLConfig(AppConfig):
    name = 'mjml'
    verbose_name = 'Use MJML in Django templates'

    def ready(self):
        check_mjml_command()
