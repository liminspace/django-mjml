from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from mjml.backend import mjml_backends
from mjml.backends.cmd import CmdBackend
from testprj.tools import MJMLFixtures, render_tpl


@override_settings(
    MJML={
        "default": {
            "BACKEND": "mjml.backends.cmd.CmdBackend",
            "OPTIONS": {
                "exec_cmd": str(
                    Path(settings.BASE_DIR) / "node_modules" / ".bin" / "mjml"
                ),
            },
        }
    }
)
class TestBackendCmd(MJMLFixtures, SimpleTestCase):
    def test_backend_usage(self) -> None:

        self.assertIsInstance(mjml_backends["default"], CmdBackend)

    def test_simple(self) -> None:
        html = render_tpl(self.TPLS["simple"])
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("20px ", html)
        self.assertIn("Test title", html)
        self.assertIn("Test button", html)

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
        html = render_tpl(
            self.TPLS["with_text_context_and_unicode"], {"text": unicode_text}
        )
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn(unicode_text, html)
        self.assertIn("©", html)

    @override_settings(
        MJML={
            "default": {
                "BACKEND": "mjml.backends.cmd.CmdBackend",
                "OPTIONS": {
                    "exec_cmd": ["echo", "wrong", "result"],
                    "check_on_startup": True,
                },
            }
        }
    )
    def test_complex_invalid_exec_cmd(self):
        with self.assertRaises(ImproperlyConfigured):
            mjml_backends["default"]

    @override_settings(
        MJML={
            "default": {
                "BACKEND": "mjml.backends.cmd.CmdBackend",
                "OPTIONS": {
                    "exec_cmd": "/not-mjml",
                    "check_on_startup": True,
                },
            }
        }
    )
    def test_startup_check_failure(self):
        with self.assertRaises(ImproperlyConfigured):
            mjml_backends["default"]

    @override_settings(
        MJML={
            "default": {
                "BACKEND": "mjml.backends.cmd.CmdBackend",
                "OPTIONS": {
                    "exec_cmd": "/not-mjml",
                    "check_on_startup": False,
                },
            }
        }
    )
    def test_startup_check_failure_ignore(self):
        mjml_backends["default"]

    @override_settings(
        MJML_BACKEND_MODE="cmd",
        MJML_EXEC_CMD=str(Path(settings.BASE_DIR) / "node_modules" / ".bin" / "mjml"),
        MJML_CHECK_CMD_ON_STARTUP=True,
    )
    def test_settings_level_config(self):
        del settings.MJML

        with self.assertRaises(AttributeError):
            settings.MJML

        self.assertIsInstance(mjml_backends["default"], CmdBackend)
        self.assertEqual(
            mjml_backends["default"].exec_cmd, [settings.MJML_EXEC_CMD, "-i", "-s"]
        )
        self.assertTrue(mjml_backends["default"].check_on_startup)
