from __future__ import absolute_import
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

# httpserver backend mode configs
MJML_HTTPSERVERS = getattr(settings, 'MJML_HTTPSERVERS', [{
    'URL': 'https://api.mjml.io/v1/render',
    'HTTP_AUTH': None,  # None (default) or ('login', 'password')
}])
assert isinstance(MJML_HTTPSERVERS, (list, tuple))
for t in MJML_HTTPSERVERS:
    assert isinstance(t, dict)
    assert 'URL' in t and isinstance(t['URL'], str)
    if 'HTTP_AUTH' in t:
        http_auth = t['HTTP_AUTH']
        assert isinstance(http_auth, (type(None), list, tuple))
        if http_auth is not None:
            assert len(http_auth) == 2 and isinstance(http_auth[0], str) and isinstance(http_auth[1], str)
