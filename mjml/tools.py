from . import settings as mjml_settings


def get_mjml_popen_args():
    cmd = mjml_settings.MJML_EXEC_PATH
    if not isinstance(cmd, list):
        cmd = [cmd]
    cmd.extend(['-i', '-s'])
    return cmd
