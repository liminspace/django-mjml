from django.conf import settings

MJML_RENDERER = getattr(settings, "MJML_RENDERER", None)

# old deprecated settings

MJML_BACKEND_MODE = getattr(settings, "MJML_BACKEND_MODE", None)
if MJML_BACKEND_MODE is not None and MJML_BACKEND_MODE not in {"cmd", "tcpserver", "httpserver"}:
    err_msg = f"Invalid value of MJML_BACKEND_MODE: {MJML_BACKEND_MODE}; allowed values: cmd, tcpserver, httpserver"
    raise ValueError(err_msg)

# cmd backend mode configs
MJML_EXEC_CMD = getattr(settings, "MJML_EXEC_CMD", None)
MJML_CHECK_CMD_ON_STARTUP = getattr(settings, "MJML_CHECK_CMD_ON_STARTUP", None)

# tcpserver backend mode configs
MJML_TCPSERVERS = getattr(settings, "MJML_TCPSERVERS", None)
if MJML_TCPSERVERS is not None:
    if not isinstance(MJML_TCPSERVERS, (list, tuple)):
        err_msg = f"Invalid type of MJML_TCPSERVERS: {type(MJML_TCPSERVERS)}; allowed types: list, tuple"
        raise ValueError(err_msg)

    for t in MJML_TCPSERVERS:
        if not (isinstance(t, (list, tuple)) and len(t) == 2 and isinstance(t[0], str) and isinstance(t[1], int)):
            err_msg = "Invalid value of MJML_TCPSERVERS"
            raise ValueError(err_msg)

# httpserver backend mode configs
MJML_HTTPSERVERS = getattr(settings, "MJML_HTTPSERVERS", None)
if MJML_HTTPSERVERS is not None:
    if not isinstance(MJML_HTTPSERVERS, (list, tuple)):
        err_msg = f"Invalid type of MJML_HTTPSERVERS: {type(MJML_HTTPSERVERS)}; allowed types: list, tuple"
        raise ValueError(err_msg)

    for t in MJML_HTTPSERVERS:
        if not (isinstance(t, dict) and "URL" in t and isinstance(t["URL"], str)):
            err_msg = "Invalid value of MJML_HTTPSERVERS"
            raise ValueError(err_msg)

        if "HTTP_AUTH" in t:
            http_auth = t["HTTP_AUTH"]
            if not isinstance(http_auth, (type(None), list, tuple)):
                err_msg = "Invalid value of HTTP_AUTH in MJML_HTTPSERVERS"
                raise ValueError(err_msg)
            if http_auth is not None and not (
                len(http_auth) == 2 and isinstance(http_auth[0], str) and isinstance(http_auth[1], str)
            ):
                err_msg = "Invalid value of HTTP_AUTH in MJML_HTTPSERVERS"
                raise ValueError(err_msg)
