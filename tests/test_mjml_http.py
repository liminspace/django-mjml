import subprocess
import time
from unittest.mock import patch

from requests.auth import HTTPBasicAuth
from django.test import TestCase
from mjml import settings as mjml_settings
from mjml.tools import requests

from .tests import safe_change_mjml_settings, render_tpl

try:
    from urllib.parse import urlparse
except ModuleNotFoundError:
    from urlparse import urlparse


class TestMJMLHTTPServer(TestCase):
    server_process = None
    url = None

    @classmethod
    def setUpClass(cls):
        super(TestMJMLHTTPServer, cls).setUpClass()
        parsed = urlparse(mjml_settings.MJML_HTTP_SERVER)
        host, port = parsed.netloc.split(":")
        cls.server_process = subprocess.Popen(
            ["mjml-http-server", "--host={}".format(host), "--port={}".format(port)]
        )
        cls.url = "{}/v1/render".format(mjml_settings.MJML_HTTP_SERVER)
        cls.settings_manager = safe_change_mjml_settings()
        cls.settings_manager.__enter__()
        mjml_settings.MJML_BACKEND_MODE = "httpserver"
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        super(TestMJMLHTTPServer, cls).tearDownClass()
        cls.server_process.terminate()
        cls.settings_manager.__exit__(None, None, None)

    def test_simple(self):
        tpl = valid_tpl()
        html = render_tpl(tpl)
        self.assertIn("<html ", html)
        self.assertIn("<body", html)
        self.assertIn("Test button", html)

    def test_raises_on_compilation_errors(self):
        tpl = """
            {% mjml %}
            <mjml>
                <mj-body>
                    <mj-button>
                </mj-body>
            </mjml>
            {% endmjml %}
        """
        with self.assertRaises(RuntimeError) as cm:
            html = render_tpl(tpl)

        self.assertIn(
            (
                "(mj-button) — mj-button cannot be used inside "
                "mj-body, only inside: mj-attributes, mj-column, mj-hero"
            ),
            str(cm.exception),
        )

    @patch.object(requests, "post", wraps=requests.post)
    def test_uses_basic_auth(self, post):
        mjml_settings.MJML_HTTP_BASIC_AUTH_USERNAME = 'foo'
        mjml_settings.MJML_HTTP_BASIC_AUTH_PASSWORD = 'bar'
        tpl = valid_tpl()
        render_tpl(tpl)
        _, kwargs = post.call_args
        expected_auth = HTTPBasicAuth('foo', 'bar')
        self.assertEqual(kwargs["auth"], expected_auth)


def valid_tpl():
    return """
        {% mjml %}
          <mjml>
            <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-button>Test button</mj-button>
                        </mj-column>
                    </mj-section>

                </mj-container>
            </mj-body>
          </mjml>
        {% endmjml %}
    """
