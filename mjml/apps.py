from django.apps import AppConfig

from mjml.backend import MJMLBackendHandler, mjml_backends


class MJMLConfig(AppConfig):
    name = "mjml"
    verbose_name = "Use MJML in Django templates"

    def ready(self) -> None:
        from django.core.signals import setting_changed as core_setting_changed
        from django.test.signals import setting_changed as test_setting_changed

        core_setting_changed.connect(self._reset_handler)
        test_setting_changed.connect(self._reset_handler)

    @staticmethod
    def _reset_handler(*, setting, **kwargs):
        """
        The ConnectionHandler used for the backend handling
        caches its settings and connections.
        So during testing this means that if you use override_settings
        to change the backend it won't actually change.
        So this watches for changes to the MJML settings and resets the cache
        on the mjml_backends instance.
        """
        if setting in MJMLBackendHandler.WATCHED_SETTINGS:
            from asgiref.local import Local

            # While mjml_backends.settings is using @cached_property
            # the configure_settings also stores the settings in _settings
            # So need to make sure both are reset otherwise the connections are removed
            # but the settings will be the same
            mjml_backends._settings = None
            mjml_backends.__dict__.pop("settings", None)
            # Delete the default attribute directly instead of replacing Local

            try:
                delattr(mjml_backends._connections, "default")
            except AttributeError:
                pass
            mjml_backends._connections = Local(mjml_backends.thread_critical)
