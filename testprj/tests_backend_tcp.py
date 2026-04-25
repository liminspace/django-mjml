import subprocess
import time
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from mjml.backend import mjml_backends
from mjml.backends.tcp import TcpBackend
from testprj.tools import MJMLFixtures, render_tpl

TCP_SERVERS = [
    ("127.0.0.1", 28101),
    ("127.0.0.1", 28102),
]


@override_settings(
    MJML={
        "default": {
            "BACKEND": "mjml.backends.tcp.TcpBackend",
            "OPTIONS": {"servers": TCP_SERVERS},
        }
    }
)
class TestBackendTcp(MJMLFixtures, SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._processes: list[subprocess.Popen] = []

        root_dir = Path(settings.BASE_DIR)
        tcpserver_path = root_dir / "mjml-tcpserver" / "tcpserver.js"

        for host, port in TCP_SERVERS:
            p = subprocess.Popen(
                [
                    "node",
                    str(tcpserver_path.resolve()),
                    f"--port={port}",
                    f"--host={host}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        while cls._processes:
            p = cls._processes.pop()
            p.terminate()

    def test_backend_usage(self) -> None:
        self.assertIsInstance(mjml_backends["default"], TcpBackend)

    def test_simple(self) -> None:
        html = render_tpl(self.TPLS["simple"])

        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("20px ", html)
        self.assertIn("Test title", html)
        self.assertIn("Test button", html)

        with self.assertRaises(RuntimeError):
            render_tpl("""
                {% mjml %}
                    123
                {% endmjml %}
            """)

    def test_large_tpl(self) -> None:
        html = render_tpl(
            self.TPLS["with_text_context"],
            {
                "text": "[START]" + ("1 2 3 4 5 6 7 8 9 0 " * 410 * 1024) + "[END]",
            },
        )
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("[START]", html)
        self.assertIn("[END]", html)

    def test_unicode(self) -> None:
        html = render_tpl(
            self.TPLS["with_text_context_and_unicode"],
            {
                "text": self.TEXTS["unicode"],
            },
        )
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("Український текст", html)
        self.assertIn(self.TEXTS["unicode"], html)
        self.assertIn("©", html)

    @override_settings(
        MJML_BACKEND_MODE="tcpserver",
        MJML_TCPSERVERS=TCP_SERVERS,
    )
    def test_settings_level_config(self):
        del settings.MJML

        self.assertIsInstance(mjml_backends["default"], TcpBackend)
        self.assertEqual(
            mjml_backends["default"].servers,
            TCP_SERVERS,
        )
