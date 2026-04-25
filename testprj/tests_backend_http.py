import json
import subprocess
import time
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import urlparse

import requests.auth
from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.utils.encoding import force_bytes

from mjml.backend import mjml_backends
from mjml.backends.http import HttpBackend
from testprj.tools import MJMLFixtures, render_tpl

HTTP_SERVERS = [
    {
        "url": "http://127.0.0.1:38101/v1/render",
    },
    {
        "url": "http://127.0.0.1:38102/v1/render",
    },
]


@override_settings(
    MJML={
        "default": {
            "BACKEND": "mjml.backends.http.HttpBackend",
            "OPTIONS": {"servers": HTTP_SERVERS},
        }
    }
)
class TestBackendHttp(MJMLFixtures, SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._processes: list[subprocess.Popen] = []

        for server_conf in HTTP_SERVERS:
            parsed = urlparse(server_conf["url"])
            host, port = parsed.netloc.split(":")
            p = subprocess.Popen(
                [
                    str(
                        (
                            Path(settings.BASE_DIR)
                            / "node_modules"
                            / ".bin"
                            / "mjml-http-server"
                        ).resolve()
                    ),
                    f"--host={host}",
                    f"--port={port}",
                    "--max-body=8500kb",
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
        self.assertIsInstance(mjml_backends["default"], HttpBackend)

    def test_simple(self) -> None:
        html = render_tpl(self.TPLS["simple"])
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("20px ", html)
        self.assertIn("Test title", html)
        self.assertIn("Test button", html)

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

    def test_http_server_error(self) -> None:
        with self.assertRaises(RuntimeError) as cm:
            render_tpl("""
                {% mjml %}
                    <mjml>
                        <mj-body>
                            <mj-button>
                        </mj-body>
                    </mjml>
                {% endmjml %}
            """)
        self.assertIn(" Tag: mj-button Message: mj-button ", str(cm.exception))

    @override_settings(
        MJML={
            "default": {
                "BACKEND": "mjml.backends.http.HttpBackend",
                "OPTIONS": {
                    "servers": [
                        {
                            **server,
                            "auth": (
                                "testuser",
                                "testpassword",
                            ),
                        }
                        for server in HTTP_SERVERS
                    ]
                },
            }
        }
    )
    @mock.patch("requests.post")
    def test_http_auth(self, post_mock) -> None:
        response = requests.Response()
        response.status_code = 200
        response._content = force_bytes(
            json.dumps(
                {
                    "errors": [],
                    "html": "html_string",
                    "mjml": "mjml_string",
                    "mjml_version": "4.5.1",
                }
            )
        )
        response.encoding = "utf-8"
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Content-Length"] = len(response._content)
        post_mock.return_value = response

        render_tpl(self.TPLS["simple"])

        self.assertTrue(post_mock.called)
        self.assertIn("auth", post_mock.call_args[1])
        self.assertIsInstance(
            post_mock.call_args[1]["auth"], requests.auth.HTTPBasicAuth
        )
        self.assertEqual(post_mock.call_args[1]["auth"].username, "testuser")
        self.assertEqual(post_mock.call_args[1]["auth"].password, "testpassword")

    @unittest.skip("to run locally")
    def test_public_api(self) -> None:
        html = render_tpl(
            self.TPLS["with_text_context_and_unicode"],
            {
                "text": self.TEXTS["unicode"]
                + " [START]"
                + ("1 2 3 4 5 6 7 8 9 0 " * 1024)
                + "[END]",
            },
        )
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("Український текст", html)
        self.assertIn(self.TEXTS["unicode"], html)
        self.assertIn("©", html)
        self.assertIn("[START]", html)
        self.assertIn("[END]", html)

        with self.assertRaises(RuntimeError) as cm:
            render_tpl("""
                {% mjml %}
                    <mjml>
                        <mj-body>
                            <mj-button>
                        </mj-body>
                    </mjml>
                {% endmjml %}
            """)
        self.assertIn(" Tag: mj-button Message: mj-button ", str(cm.exception))

    @override_settings(
        MJML_BACKEND_MODE="httpserver",
        MJML_HTTPSERVERS=[{"URL": server["url"]} for server in HTTP_SERVERS],
    )
    def test_settings_level_config(self):
        del settings.MJML

        self.assertIsInstance(mjml_backends["default"], HttpBackend)

        self.assertIn(
            HTTP_SERVERS[0]["url"],
            [server["url"] for server in mjml_backends["default"].servers],
        )
