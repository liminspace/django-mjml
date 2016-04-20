import subprocess
from . import settings as mjml_settings


def mjml_render(mjml_code):
    cmd_args = mjml_settings.MJML_EXEC_CMD
    if not isinstance(cmd_args, list):
        cmd_args = [cmd_args]
        cmd_args.extend(['-i', '-s'])

    try:
        p = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        html = p.communicate(mjml_code.encode('utf8'))[0]
    except (IOError, OSError) as e:
        raise RuntimeError(
            'Problem to run command "{}"\n'.format(' '.join(cmd_args)) +
            '{}\n'.format(e) +
            'Check that mjml is installed and allow permissions for execute.\n' +
            'See https://github.com/mjmlio/mjml#installation'
        )
    return html
