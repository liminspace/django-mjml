from copy import copy

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.connection import BaseConnectionHandler, ConnectionProxy
from django.utils.module_loading import import_string

DEFAULT_TASK_BACKEND_ALIAS = "default"


class InvalidMJMLBackend(ImproperlyConfigured):
    """The provided Task backend is invalid."""


class MJMLBackendHandler(BaseConnectionHandler):
    """
    The Connection/Backend Handler looks after
    loading the class of the backend and holding it as a connection

    The conversion of django settings to connection options/settings
    is managed through the handler and applies the appropriate settings
    to the configured backends
    """

    settings_name = "MJML"

    # The BaseConnectionHandler has a cached_property
    # on the settings property which means that during testing
    # the cache is kept between settings, so you can't easily move between
    # backends.
    # To get around this the AppConfig includes a signal handler which
    # will reset the cache on the mjml_backends singleton instance
    # These are the settings that we look for in the signal callback
    WATCHED_SETTINGS = [
        "MJML",
        "MJML_BACKEND_MODE",
        "MJML_EXEC_CMD",
        "MJML_CHECK_CMD_ON_STARTUP",
        "MJML_HTTPSERVERS",
        "MJML_TCPSERVERS",
    ]

    def configure_settings(self, settings):
        if settings is None:
            if hasattr(django_settings, self.settings_name):
                return getattr(django_settings, self.settings_name)

            # Handles the existing base settings file configuration by converting
            # these settings into the configuration for the default backend
            if hasattr(django_settings, "MJML_BACKEND_MODE"):
                legacy_backend = {
                    "BACKEND": "",
                    "OPTIONS": {},
                }

                mjml_backend_name = getattr(django_settings, "MJML_BACKEND_MODE", "cmd")

                if mjml_backend_name == "cmd":
                    legacy_backend["BACKEND"] = "mjml.backends.cmd.CmdBackend"
                elif mjml_backend_name == "tcpserver":
                    legacy_backend["BACKEND"] = "mjml.backends.tcp.TcpBackend"
                elif mjml_backend_name == "httpserver":
                    legacy_backend["BACKEND"] = "mjml.backends.http.HttpBackend"
                else:
                    raise ImproperlyConfigured(
                        f"MJML_BACKEND_MODE can only be one of cmd, tcpserver or httpserver - {mjml_backend_name} was provided\n"
                        "If you want to use your own class backend use the MJML setting instead"
                    )

                if mjml_backend_name == "cmd":
                    if hasattr(django_settings, "MJML_EXEC_CMD"):
                        legacy_backend["OPTIONS"]["exec_cmd"] = copy(
                            django_settings.MJML_EXEC_CMD
                        )
                    if hasattr(django_settings, "MJML_CHECK_CMD_ON_STARTUP"):
                        legacy_backend["OPTIONS"]["check_on_startup"] = copy(
                            django_settings.MJML_CHECK_CMD_ON_STARTUP
                        )

                if mjml_backend_name == "httpserver":
                    if not hasattr(django_settings, "MJML_HTTPSERVERS"):
                        raise ImproperlyConfigured(
                            "MJML_BACKEND_MODE is set to httpserver but the MJML_HTTPSERVERS setting has not been provided\n"
                            'Add MJML_HTTPSERVERS to your settings with a list of the http servers to use in the format of [{"URL": "<server url>"}]'
                        )
                    else:
                        legacy_backend["OPTIONS"]["servers"] = [
                            {"url": server["URL"], "auth": server.get("AUTH", None)}
                            for server in django_settings.MJML_HTTPSERVERS[:]
                        ]

                if mjml_backend_name == "tcpserver":
                    if not hasattr(django_settings, "MJML_TCPSERVERS"):
                        raise ImproperlyConfigured(
                            "MJML_BACKEND_MODE is set to httpserver but the MJML_TCPSERVERS setting has not been provided\n"
                            'Add MJML_TCPSERVERS to your settings with a list of the tcp servers as a tuple of their IP/Hostname and port [("<ip/hostname>", <port>)]'
                        )
                    else:
                        legacy_backend["OPTIONS"]["servers"] = (
                            django_settings.MJML_TCPSERVERS[:]
                        )

                return {
                    DEFAULT_TASK_BACKEND_ALIAS: legacy_backend,
                }

            # The default settings which is to use the CmdBackend
            return {
                DEFAULT_TASK_BACKEND_ALIAS: {
                    "BACKEND": "mjml.backends.cmd.CmdBackend",
                    "OPTIONS": {},
                }
            }

        return settings

    def create_connection(self, alias):
        params = self.settings[alias]
        backend = params["BACKEND"]

        try:
            backend_cls = import_string(backend)
        except ImportError as e:
            raise InvalidMJMLBackend(f"Could not find backend '{backend}': {e}") from e

        conn = backend_cls(alias=alias, params=params)

        return conn

    def __getitem__(self, alias):
        conn = super().__getitem__(alias)

        # as items are loaded into the handler we can run the same startup
        # check that is currently in place
        # This will apply to all backends not just Cmd
        if conn.check_on_startup and not getattr(conn, "_startup_checked", False):
            conn.check()
            conn._startup_checked = True
        return conn


mjml_backends = MJMLBackendHandler()
default_mjml_backend = ConnectionProxy(mjml_backends, DEFAULT_TASK_BACKEND_ALIAS)
