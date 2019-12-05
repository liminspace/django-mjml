# coding=utf-8
from __future__ import absolute_import
import os
import copy
import subprocess
import time
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from contextlib import contextmanager
from django.conf import settings
from django.template import Template, Context
from mjml import settings as mjml_settings
from mjml import tools


def get_mjml_version():
    env_ver = os.environ.get('MJML_VERSION', None)
    if env_ver:
        try:
            return int(env_ver.split('.')[0])
        except (ValueError, TypeError, IndexError):
            pass
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


def render_tpl(tpl, context=None):
    if get_mjml_version() >= 4:
        tpl = tpl.replace('<mj-container>', '').replace('</mj-container>', '')
    return Template('{% load mjml %}' + tpl).render(Context(context))


class MJMLServers(object):
    SERVER_TYPE = NotImplemented  # tcpserver, httpserver
    _processes = []

    @classmethod
    def _terminate_processes(cls):
        while cls._processes:
            p = cls._processes.pop()
            p.terminate()

    @classmethod
    def _start_tcp_servers(cls):
        root_dir = os.path.dirname(settings.BASE_DIR)
        tcpserver_path = os.path.join(root_dir, 'mjml', 'node', 'tcpserver.js')
        env = os.environ.copy()
        env['NODE_PATH'] = root_dir
        for host, port in mjml_settings.MJML_TCPSERVERS:
            p = subprocess.Popen([
                'node',
                tcpserver_path,
                '--port={}'.format(port),
                '--host={}'.format(host),
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def _stop_tcp_servers(cls):
        cls._terminate_processes()

    @classmethod
    def _start_http_servers(cls):
        env = os.environ.copy()
        for server_conf in mjml_settings.MJML_HTTPSERVERS:
            parsed = urlparse(server_conf['URL'])
            host, port = parsed.netloc.split(':')
            p = subprocess.Popen([
                'mjml-http-server',
                '--host={}'.format(host),
                '--port={}'.format(port),
                '--max-body=8500kb',
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def _stop_http_servers(cls):
        cls._terminate_processes()

    @classmethod
    def setUpClass(cls):
        super(MJMLServers, cls).setUpClass()
        if cls.SERVER_TYPE == 'tcpserver':
            cls._start_tcp_servers()
        elif cls.SERVER_TYPE == 'httpserver':
            cls._start_http_servers()
        else:
            raise RuntimeError('Invalid SERVER_TYPE: {}', cls.SERVER_TYPE)

    @classmethod
    def tearDownClass(cls):
        if cls.SERVER_TYPE == 'tcpserver':
            cls._stop_tcp_servers()
        elif cls.SERVER_TYPE == 'httpserver':
            cls._stop_http_servers()
        else:
            raise RuntimeError('Invalid SERVER_TYPE: {}', cls.SERVER_TYPE)
        super(MJMLServers, cls).tearDownClass()


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
        'smile': u'\u263a',
        'checkmark': u'\u2713',
        'candy': u'\U0001f36d',  # b'\xf0\x9f\x8d\xad'.decode('utf-8')
    }
    TEXTS = {
        'unicode': SYMBOLS['smile'] + SYMBOLS['checkmark'] + SYMBOLS['candy'],
    }
