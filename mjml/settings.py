from django.conf import settings

MJML_BACKEND_MODE = getattr(settings, 'MJML_BACKEND_MODE', 'cmd')
assert MJML_BACKEND_MODE in ('cmd', 'tcpserver')

# cmd backend mode configs
MJML_EXEC_CMD = getattr(settings, 'MJML_EXEC_CMD', 'mjml')

# tcpserver backend mode configs
MJML_TCPSERVERS = getattr(settings, 'MJML_TCPSERVERS', [('127.0.0.1', 28101)])
assert isinstance(MJML_TCPSERVERS, (list, tuple))
for t in MJML_TCPSERVERS:
    assert isinstance(t, (list, tuple)) and len(t) == 2 and isinstance(t[0], str) and isinstance(t[1], int)
