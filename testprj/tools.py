from typing import Any, Dict, Optional

from django.template import Context, Template


def render_tpl(tpl: str, context: Optional[Dict[str, Any]] = None) -> str:
    return Template("{% load mjml %}" + tpl).render(Context(context))


class MJMLFixtures:
    TPLS = {
        "simple": """
            {% mjml %}
                <mjml>
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
                </mjml>
            {% endmjml %}
        """,
        "with_text_context": """
            {% mjml %}
                <mjml>
                <mj-body>
                    <mj-section>
                        <mj-column>
                            <mj-text>{{ text }}</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
        "with_text_context_and_unicode": """
            {% mjml %}
                <mjml>
                <mj-body>
                    <mj-section>
                        <mj-column>
                            <mj-text>Український текст {{ text }} ©</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
    }
    SYMBOLS = {
        "smile": "\u263a",
        "checkmark": "\u2713",
        "candy": "\U0001f36d",  # b'\xf0\x9f\x8d\xad'.decode('utf-8')
    }
    TEXTS = {
        "unicode": SYMBOLS["smile"] + SYMBOLS["checkmark"] + SYMBOLS["candy"],
    }
