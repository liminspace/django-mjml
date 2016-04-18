import copy
from contextlib import contextmanager
from django.test import TestCase
from django.template import Template, Context
from django.template.exceptions import TemplateSyntaxError
from django.core.exceptions import ImproperlyConfigured
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
    for k, v in mjml_settings.__dict__.iteritems():
        if k[:5] == 'MJML_':
            settings_bak[k] = copy.deepcopy(v)
    try:
        yield
    finally:
        for k, v in settings_bak.iteritems():
            setattr(mjml_settings, k, v)


class TestMJMLApps(TestCase):
    def test_check_mjml_command(self):
        with safe_change_mjml_settings():
            mjml_settings.MJML_EXEC_CMD = '/no_mjml_exec_test'
            with self.assertRaises(ImproperlyConfigured):
                check_mjml_command()

            mjml_settings.MJML_EXEC_CMD = ['python', '-c', 'print "wrong result for testing"', '-']
            with self.assertRaises(ImproperlyConfigured):
                check_mjml_command()


class TestMJMLTemplatetag(TestCase):
    def render_tpl(self, tpl, context=None):
        return Template('{% load mjml %}' + tpl).render(Context(context))

    def test_simple(self):
        html = self.render_tpl("""
            {% mjml %}
                <mj-body>
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
                </mj-body>
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
                <mj-body>
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
                </mj-body>
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
                <mj-body>
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
                </mj-body>
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
                    <mj-body></mj-body>
                {% endmjml %}
            """)

        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("""
                {% mjml var %}
                    <mj-body></mj-body>
                {% endmjml %}
            """, {'var': 'test'})


class TestMJMLCachebleTemplatetag(TestCase):
    def render_tpl(self, tpl, context=None):
        return Template('{% load mjml %}' + tpl).render(Context(context))

    def test_simple(self):
        html = self.render_tpl("""
            {% mjml_cacheble 3600 test_simple %}
                <mj-body>
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
                </mj-body>
            {% endmjml_cacheble %}
        """)
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn('20px ', html)
        self.assertIn('Test title', html)
        self.assertIn('Test button', html)

    def test_with_vars(self):
        context = {
            'title': 'Test title',
            'btn_label': 'Test button',
        }
        html = self.render_tpl("""
            {% mjml_cacheble 360 test_with_vars %}
                <mj-body>
                    <mj-section>
                        <mj-column>
                            <mj-image src="img/test.png"></mj-image>
                            <mj-text align="center">{{ title }}</mj-text>
                        </mj-column>
                    </mj-section>
                    <mj-section>
                        <mj-column>
                            <mj-button>{{ btn_label }}</mj-button>
                        </mj-column>
                    </mj-section>
                </mj-body>
            {% endmjml_cacheble %}
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
            {% mjml_cacheble 3600 test_with_vars %}
                <mj-body>
                    <mj-section>
                        <mj-column>
                            {# test_comment #}
                            {% for item in items %}
                                <mj-text color="#aabbcc" align="center">{{ item }}</mj-text>
                            {% endfor %}
                        </mj-column>
                    </mj-section>
                </mj-body>
            {% endmjml_cacheble %}
        """, context)
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        for item in items:
            self.assertIn(item, html)
        self.assertNotIn('test_comment', html)
        self.assertEqual(html.count('#aabbcc'), len(items))

    def test_arguments(self):
        self.render_tpl("{% mjml_cacheble 3600 test_errors use_cache='default' %}{% endmjml_cacheble %}")
        self.render_tpl("{% mjml_cacheble expire test_errors use_cache=cache_name %}{% endmjml_cacheble %}", {
            'expire': 3600,
            'cache_name': 'default',
        })
        self.render_tpl("{% mjml_cacheble t test_errors %}{% endmjml_cacheble %}", {'t': '3600'})

    def test_errors(self):
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble 3600 test_errors %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble 3600 test_errors test %}{% endmjml_cacheble %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble 3600 test_errors use_cache='default' test %}{% endmjml_cacheble %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble 3600 %}{% endmjml_cacheble %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble %}{% endmjml_cacheble %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble 3600 test_errors use_cache='none' %}{% endmjml_cacheble %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble 3600 test_errors use_cache=ttt %}{% endmjml_cacheble %}")
        with self.assertRaises(TemplateSyntaxError):
            self.render_tpl("{% mjml_cacheble no test_errors %}{% endmjml_cacheble %}", {'t': '3600'})
