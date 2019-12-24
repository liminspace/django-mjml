# coding=utf-8
from __future__ import absolute_import
from django.test import TestCase
from django.template import TemplateSyntaxError
from django.core.exceptions import ImproperlyConfigured
from mjml.apps import check_mjml_command
from mjml import settings as mjml_settings
from testprj.tools import safe_change_mjml_settings, render_tpl, MJMLFixtures


class TestMJMLApps(TestCase):
    def test_check_mjml_command(self):
        with safe_change_mjml_settings():
            mjml_settings.MJML_EXEC_CMD = '/no_mjml_exec_test'
            with self.assertRaises(ImproperlyConfigured):
                check_mjml_command()

            mjml_settings.MJML_EXEC_CMD = ['python', '-c', 'print("wrong result for testing")', '-']
            with self.assertRaises(ImproperlyConfigured):
                check_mjml_command()


class TestMJMLTemplatetag(MJMLFixtures, TestCase):
    def test_simple(self):
        html = render_tpl(self.TPLS['simple'])
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
        html = render_tpl("""
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
        html = render_tpl("""
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
            render_tpl("""
                {% mjml "var"%}
                    <mjml><mj-body><mj-container></mj-container></mj-body></mjml>
                {% endmjml %}
            """)

        with self.assertRaises(TemplateSyntaxError):
            render_tpl("""
                {% mjml var %}
                    <mjml><mj-body><mj-container></mj-container></mj-body></mjml>
                {% endmjml %}
            """, {'var': 'test'})

    def test_unicode(self):
        html = render_tpl(self.TPLS['with_text_context_and_unicode'], {'text':  self.TEXTS['unicode']})
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn(u'Український текст', html)
        self.assertIn(self.TEXTS['unicode'], html)
        self.assertIn(u'©', html)
