import copy
import os
import subprocess
import time
from contextlib import contextmanager, suppress
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from django.conf import settings
from django.template import Template, Context

from mjml import settings as mjml_settings
from mjml import tools


def get_mjml_version() -> int:
    env_ver = os.environ.get('MJML_VERSION', None)
    if env_ver:
        with suppress(ValueError, TypeError, IndexError):
            return int(env_ver.split('.')[0])

    return settings.DEFAULT_MJML_VERSION


@contextmanager
def safe_change_mjml_settings():
    """
    with safe_change_mjml_settings():
        mjml_settins.MJML_EXEC_PATH = 'other value'
        ...
    # mjml settings will be restored
    ...
    """
    settings_bak = {}
    for k, v in mjml_settings.__dict__.items():
        if k[:5] == 'MJML_':
            settings_bak[k] = copy.deepcopy(v)
    tools._cache.clear()
    try:
        yield
    finally:
        for k, v in settings_bak.items():
            setattr(mjml_settings, k, v)
        tools._cache.clear()


def render_tpl(tpl: str, context: Optional[Dict[str, Any]] = None) -> str:
    if get_mjml_version() >= 4:
        tpl = tpl.replace('<mj-container>', '').replace('</mj-container>', '')
    return Template('{% load mjml %}' + tpl).render(Context(context))


class MJMLServers:
    SERVER_TYPE = NotImplemented  # tcpserver, httpserver
    _processes = []

    @classmethod
    def _terminate_processes(cls) -> None:
        while cls._processes:
            p = cls._processes.pop()
            p.terminate()

    @classmethod
    def _start_tcp_servers(cls) -> None:
        root_dir = os.path.dirname(settings.BASE_DIR)
        tcpserver_path = os.path.join(root_dir, 'mjml-tcpserver', 'tcpserver.js')
        env = os.environ.copy()
        env['NODE_PATH'] = root_dir
        for host, port in mjml_settings.MJML_TCPSERVERS:
            p = subprocess.Popen([
                'node',
                tcpserver_path,
                f'--port={port}',
                f'--host={host}',
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def _stop_tcp_servers(cls) -> None:
        cls._terminate_processes()

    @classmethod
    def _start_http_servers(cls) -> None:
        env = os.environ.copy()
        for server_conf in mjml_settings.MJML_HTTPSERVERS:
            parsed = urlparse(server_conf['URL'])
            host, port = parsed.netloc.split(':')
            p = subprocess.Popen([
                'mjml-http-server',
                f'--host={host}',
                f'--port={port}',
                '--max-body=8500kb',
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def _stop_http_servers(cls) -> None:
        cls._terminate_processes()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        if cls.SERVER_TYPE == 'tcpserver':
            cls._start_tcp_servers()
        elif cls.SERVER_TYPE == 'httpserver':
            cls._start_http_servers()
        else:
            raise RuntimeError('Invalid SERVER_TYPE: {}', cls.SERVER_TYPE)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.SERVER_TYPE == 'tcpserver':
            cls._stop_tcp_servers()
        elif cls.SERVER_TYPE == 'httpserver':
            cls._stop_http_servers()
        else:
            raise RuntimeError('Invalid SERVER_TYPE: {}', cls.SERVER_TYPE)
        super().tearDownClass()


class MJMLFixtures:
    TPLS = {
        'simple': """
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-image src="img/test.png"></mj-image>
                            <mj-text font-size="20px" align="center">Test title</mj-text>
                        </mj-column>
                    </mj-section>
                    <mj-section>
                        <mj-column>
                            <mj-button background-color="#ffcc00" font-size="15px">Test button</mj-button>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
        'with_text_context': """
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-text>{{ text }}</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
        'with_text_context_and_unicode': """
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-text>Український текст {{ text }} ©</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
    }
    SYMBOLS = {
        'smile': '\u263a',
        'checkmark': '\u2713',
        'candy': '\U0001f36d',  # b'\xf0\x9f\x8d\xad'.decode('utf-8')
    }
    TEXTS = {
        'unicode': SYMBOLS['smile'] + SYMBOLS['checkmark'] + SYMBOLS['candy'],
    }
