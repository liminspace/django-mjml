from django.conf import settings

MJML_BACKEND_MODE = getattr(settings, 'MJML_BACKEND_MODE', 'cmd')
assert MJML_BACKEND_MODE in ('cmd', 'tcpserver', 'httpserver')

# cmd backend mode configs
MJML_EXEC_CMD = getattr(settings, 'MJML_EXEC_CMD', 'mjml')
MJML_CHECK_CMD_ON_STARTUP = getattr(settings, 'MJML_CHECK_CMD_ON_STARTUP', True)

# tcpserver backend mode configs
MJML_TCPSERVERS = getattr(settings, 'MJML_TCPSERVERS', [('127.0.0.1', 28101)])
assert isinstance(MJML_TCPSERVERS, (list, tuple))
for t in MJML_TCPSERVERS:
    assert isinstance(t, (list, tuple)) and len(t) == 2 and isinstance(t[0], str) and isinstance(t[1], int)

# http server mode configs
MJML_HTTP_SERVER = getattr(settings, 'MJML_HTTP_SERVER', 'http://127.0.0.1:15500')
MJML_HTTP_BASIC_AUTH_USERNAME = getattr(settings, 'MJML_HTTP_BASIC_AUTH_USERNAME', None)
MJML_HTTP_BASIC_AUTH_PASSWORD = getattr(settings, 'MJML_HTTP_BASIC_AUTH_PASSWORD', None)
