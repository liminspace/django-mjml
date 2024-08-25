import warnings
from typing import Any, Dict

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from mjml.backends.base import BaseRendererBackend
from mjml.backends.exceptions import RendererBackendCheckFailedError


class MJMLConfig(AppConfig):
    name = "mjml"
    verbose_name = "Use MJML in Django templates"
    _renderer: BaseRendererBackend

    def ready(self) -> None:
        renderer_params = self._get_renderer_params()
        renderer_class = import_string(renderer_params["BACKEND"])
        self._renderer = renderer_class.create(params=renderer_params)

        try:
            self._renderer.check()
        except RendererBackendCheckFailedError as e:
            raise ImproperlyConfigured(e) from e

    def get_renderer(self) -> BaseRendererBackend:
        return self._renderer

    @classmethod
    def _get_renderer_params(cls) -> Dict[str, Any]:
        from mjml import settings as mjml_settings

        if mjml_settings.MJML_RENDERER:
            return mjml_settings.MJML_RENDERER

        if mjml_settings.MJML_BACKEND_MODE:
            warnings.warn(
                "you should use MJML_RENDERER setting; the other MJML_* ones are deprecated",
                DeprecationWarning,
                stacklevel=1,
            )
            if mjml_settings.MJML_BACKEND_MODE == "cmd":
                return {
                    "BACKEND": "mjml.backends.CMDBackend",
                    "CMD_ARGS": mjml_settings.MJML_EXEC_CMD or "mjml",
                    "CHECK_ON_STARTUP": (
                        True
                        if mjml_settings.MJML_CHECK_CMD_ON_STARTUP is None
                        else mjml_settings.MJML_CHECK_CMD_ON_STARTUP
                    ),
                }
            elif mjml_settings.MJML_BACKEND_MODE == "tcpserver":
                return {
                    "BACKEND": "mjml.backends.TCPServerBackend",
                    "SERVERS": mjml_settings.MJML_TCPSERVERS or [("127.0.0.1", 28101)],
                }
            elif mjml_settings.MJML_BACKEND_MODE == "httpserver":
                return {
                    "BACKEND": "mjml.backends.RequestsHTTPServerBackend",
                    "SERVERS": [
                        {
                            "URL": t["URL"],
                            "AUTH": t.get("HTTP_AUTH", None),
                        }
                        for t in mjml_settings.MJML_HTTPSERVERS
                        or [
                            {
                                "URL": "https://api.mjml.io/v1/render",
                                "HTTP_AUTH": None,  # None (default) or ('login', 'password')
                            }
                        ]
                    ],
                }
            else:
                RuntimeError("Invalid MJML settings")

        # default settings
        return {
            "BACKEND": "mjml.backends.CMDBackend",
            "CMD_ARGS": "mjml",
            "CHECK_ON_STARTUP": True,
        }
