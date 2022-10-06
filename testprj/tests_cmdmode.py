from django.test import TestCase

from testprj.tools import render_tpl, MJMLFixtures


class TestMJMLCMDMode(MJMLFixtures, TestCase):
    def test_big_email(self) -> None:
        big_text = '[START]' + ('Big text. ' * 820 * 1024) + '[END]'
        html = render_tpl(self.TPLS['with_text_context'], {'text': big_text})
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn('Big text. ', html)
        self.assertIn('[START]', html)
        self.assertIn('[END]', html)
        self.assertIn('</body>', html)
        self.assertIn('</html>', html)

    def test_unicode(self) -> None:
        smile = '\u263a'
        checkmark = '\u2713'
        candy = '\U0001f36d'
        unicode_text = smile + checkmark + candy
        html = render_tpl(self.TPLS['with_text_context_and_unicode'], {'text': unicode_text})
        self.assertIn('<html ', html)
        self.assertIn('<body', html)
        self.assertIn(unicode_text, html)
        self.assertIn('©', html)
