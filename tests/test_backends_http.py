import json
import unittest
from typing import ContextManager
from unittest import mock

import requests.auth
from django.test import TestCase
from django.utils.encoding import force_bytes

from mjml import settings as mjml_settings

from .tools import MJMLFixtures, MJMLServers, render_tpl, safe_change_mjml_settings


class TestMJMLHTTPServer(MJMLFixtures, MJMLServers, TestCase):
    SERVER_TYPE = "httpserver"
    _settings_manager: ContextManager

    @classmethod
    def setUpClass(cls) -> None:
        cls._settings_manager = safe_change_mjml_settings()
        mjml_app_config = cls._settings_manager.__enter__()
        mjml_settings.MJML_BACKEND_MODE = cls.SERVER_TYPE
        mjml_settings.MJML_RENDERER = None
        mjml_app_config.ready()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls._settings_manager.__exit__(None, None, None)

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

    @mock.patch("requests.post")
    def test_http_auth(self, post_mock) -> None:
        with safe_change_mjml_settings() as mjml_app_config:
            for server_conf in mjml_settings.MJML_HTTPSERVERS:  # type: ignore  # TODO: fix
                server_conf["HTTP_AUTH"] = ("testuser", "testpassword")
            mjml_app_config.ready()

            response = requests.Response()
            response.status_code = 200
            content = force_bytes(
                json.dumps(
                    {
                        "errors": [],
                        "html": "html_string",
                        "mjml": "mjml_string",
                        "mjml_version": "4.5.1",
                    },
                ),
            )
            response._content = content
            response.encoding = "utf-8"
            response.headers["Content-Type"] = "text/html; charset=utf-8"
            response.headers["Content-Length"] = str(len(content))
            post_mock.return_value = response

            render_tpl(self.TPLS["simple"])

            self.assertTrue(post_mock.called)
            self.assertIn("auth", post_mock.call_args[1])
            self.assertIsInstance(post_mock.call_args[1]["auth"], requests.auth.HTTPBasicAuth)
            self.assertEqual(post_mock.call_args[1]["auth"].username, "testuser")
            self.assertEqual(post_mock.call_args[1]["auth"].password, "testpassword")

    @unittest.skip("to run locally")
    def test_public_api(self) -> None:
        with safe_change_mjml_settings() as mjml_app_config:
            mjml_settings.MJML_HTTPSERVERS = (
                {
                    "URL": "https://api.mjml.io/v1/render",
                    "HTTP_AUTH": ("****", "****"),
                },
            )
            mjml_app_config.ready()

            html = render_tpl(
                self.TPLS["with_text_context_and_unicode"],
                {
                    "text": self.TEXTS["unicode"] + " [START]" + ("1 2 3 4 5 6 7 8 9 0 " * 1024) + "[END]",
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
