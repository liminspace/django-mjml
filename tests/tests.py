# coding=utf-8
import copy
import os
import subprocess
import time
from contextlib import contextmanager
from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from mjml.apps import check_mjml_command
from mjml import settings as mjml_settings


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
    try:
        yield
    finally:
        for k, v in settings_bak.items():
            setattr(mjml_settings, k, v)


class TestMJMLApps(TestCase):
    def test_check_mjml_command(self):
        with safe_change_mjml_settings():
            mjml_settings.MJML_EXEC_CMD = '/no_mjml_exec_test'
            with self.assertRaises(ImproperlyConfigured):
                check_mjml_command()

            mjml_settings.MJML_EXEC_CMD = ['python', '-c', 'print("wrong result for testing")', '-']
            with self.assertRaises(ImproperlyConfigured):
                check_mjml_command()


class TestMJMLTemplatetag(TestCase):
    def render_tpl(self, tpl, context=None):
        return Template('{% load mjml %}' + tpl).render(Context(context))

    def test_simple(self):
        html = self.render_tpl("""
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
        """)
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn('20px ', html)
        self.assertIn('Test title', html)
        self.assertIn('Test button', html)

    def test_with_vars(self):
        context = {
            'title': 'Test title',
            'title_size': '20px',
            'btn_label': 'Test button',
            'btn_color': '#ffcc00'
        }
        html = self.render_tpl("""
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-image src="img/test.png"></mj-image>
                            <mj-text font-size="{{ title_size }}" align="center">{{ title }}</mj-text>
                        </mj-column>
                    </mj-section>
                    <mj-section>
                        <mj-column>
                            <mj-button background-color="{{ btn_color }}" font-size="15px">{{ btn_label }}</mj-button>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """, context)
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        for val in context.values():
            self.assertIn(val, html)

    def test_with_tags(self):
        items = ['test one', 'test two', 'test three']
        context = {
            'items': items,
        }
        html = self.render_tpl("""
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
                            {# test_comment $}
                            {% for item in items %}
                                <mj-text align="center">{{ item }}</mj-text>
                            {% endfor %}
                            <mj-button background-color="#ffcc00" font-size="15px">Test button</mj-button>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """, context)
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        for item in items:
            self.assertIn(item, html)
        self.assertNotIn('test_comment', html)

    def test_error(self):
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("""
                {% mjml "var"%}
                    <mjml><mj-body><mj-container></mj-container></mj-body></mjml>
                {% endmjml %}
            """)

        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("""
                {% mjml var %}
                    <mjml><mj-body><mj-container></mj-container></mj-body></mjml>
                {% endmjml %}
            """, {'var': 'test'})

    def test_unicode(self):
        html = self.render_tpl(u"""
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-text>Український текст</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """)
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn(u'Український текст', html)


class TestMJMLTCPServer(TestCase):
    processes = []

    @classmethod
    def setUpClass(cls):
        super(TestMJMLTCPServer, cls).setUpClass()
        root_dir = os.path.dirname(settings.BASE_DIR)
        tcpserver_path = os.path.join(root_dir, 'mjml', 'node', 'tcpserver.js')
        env = os.environ.copy()
        env['NODE_PATH'] = root_dir
        for host, port in mjml_settings.MJML_TCPSERVERS:
            p = subprocess.Popen(['node', tcpserver_path, str(port), host],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            cls.processes.append(p)
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        super(TestMJMLTCPServer, cls).tearDownClass()
        while cls.processes:
            p = cls.processes.pop()
            p.terminate()

    def render_tpl(self, tpl, context=None):
        return Template('{% load mjml %}' + tpl).render(Context(context))

    def test_simple(self):
        with safe_change_mjml_settings():
            mjml_settings.MJML_BACKEND_MODE = 'tcpserver'

            html = self.render_tpl("""
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
            """)
            self.assertIn('<html ', html)
            self.assertIn('<body', html)
            self.assertIn('20px ', html)
            self.assertIn('Test title', html)
            self.assertIn('Test button', html)

            with self.assertRaises(RuntimeError):
                self.render_tpl("""
                    {% mjml %}
                        123
                    {% endmjml %}
                """)
