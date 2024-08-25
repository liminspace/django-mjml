import os
from typing import ContextManager, Dict

from django.test import TestCase

from mjml import settings as mjml_settings

from .tools import MJMLFixtures, render_tpl, safe_change_mjml_settings


class TestMJMLCMDMode(MJMLFixtures, TestCase):
    SERVER_TYPE = "cmd"
    _settings_manager: ContextManager

    @classmethod
    def setUpClass(cls) -> None:
        cls._settings_manager = safe_change_mjml_settings()
        mjml_app_config = cls._settings_manager.__enter__()
        mjml_settings.MJML_BACKEND_MODE = None
        mjml_settings.MJML_RENDERER = {
            "BACKEND": "mjml.backends.CMDBackend",
            "CMD_ARGS": mjml_settings.MJML_EXEC_CMD,
            "CMD_ENV_VARS": cls._get_test_cmd_env_vars() or None,
            "CHECK_ON_STARTUP": False,
        }
        mjml_app_config.ready()
        super().setUpClass()

    @classmethod
    def _get_test_cmd_env_vars(cls) -> Dict[str, str]:
        raw_value = os.environ.get("TEST_CMD_ENV_VARS", "").strip()
        if not raw_value:
            return {}

        env_vars = {}
        for env_var_item in raw_value.split(";"):
            key, value = env_var_item.strip().split("=", 1)
            env_vars[key.strip()] = value.strip()

        return env_vars

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls._settings_manager.__exit__(None, None, None)

    def test_big_email(self) -> None:
        big_text = "[START]" + ("Big text. " * 820 * 1024) + "[END]"
        html = render_tpl(self.TPLS["with_text_context"], {"text": big_text})
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("Big text. ", html)
        self.assertIn("[START]", html)
        self.assertIn("[END]", html)
        self.assertIn("</body>", html)
        self.assertIn("</html>", html)

    def test_unicode(self) -> None:
        smile = "\u263a"
        checkmark = "\u2713"
        candy = "\U0001f36d"
        unicode_text = smile + checkmark + candy
        html = render_tpl(self.TPLS["with_text_context_and_unicode"], {"text": unicode_text})
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn(unicode_text, html)
        self.assertIn("©", html)
