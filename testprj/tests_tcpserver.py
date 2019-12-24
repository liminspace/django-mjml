# coding=utf-8
from __future__ import absolute_import
from django.test import TestCase
from mjml import settings as mjml_settings
from testprj.tools import safe_change_mjml_settings, MJMLServers, MJMLFixtures, render_tpl


class TestMJMLTCPServer(MJMLFixtures, MJMLServers, TestCase):
    SERVER_TYPE = 'tcpserver'
    _settings_manager = None

    @classmethod
    def setUpClass(cls):
        cls._settings_manager = safe_change_mjml_settings()
        cls._settings_manager.__enter__()
        mjml_settings.MJML_BACKEND_MODE = cls.SERVER_TYPE
        super(TestMJMLTCPServer, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestMJMLTCPServer, cls).tearDownClass()
        cls._settings_manager.__exit__(None, None, None)

    def test_simple(self):
        html = render_tpl(self.TPLS['simple'])
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn('20px ', html)
        self.assertIn('Test title', html)
        self.assertIn('Test button', html)

        with self.assertRaises(RuntimeError):
            render_tpl("""
                {% mjml %}
                    123
                {% endmjml %}
            """)

    def test_large_tpl(self):
        html = render_tpl(self.TPLS['with_text_context'], {
            'text': '[START]' + ('1 2 3 4 5 6 7 8 9 0 ' * 410 * 1024) + '[END]',
        })
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn('[START]', html)
        self.assertIn('[END]', html)

    def test_unicode(self):
        html = render_tpl(self.TPLS['with_text_context_and_unicode'], {'text': self.TEXTS['unicode']})
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn(u'Український текст', html)
        self.assertIn(self.TEXTS['unicode'], html)
        self.assertIn(u'©', html)
