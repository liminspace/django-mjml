from django import template
from django.apps import apps

from mjml.apps import MJMLConfig

register = template.Library()


class MJMLRenderNode(template.Node):
    def __init__(self, nodelist, renderer):
        self.nodelist = nodelist
        self._renderer = renderer

    def render(self, context) -> str:
        mjml_source = self.nodelist.render(context)
        return self._renderer.render_mjml_to_html(mjml_source)


@register.tag
def mjml(parser, token) -> MJMLRenderNode:
    """
    Compile MJML template after render django template.

    Usage:
        {% mjml %}
            .. MJML template code ..
        {% endmjml %}
    """
    nodelist = parser.parse(("endmjml",))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) != 1:
        raise template.TemplateSyntaxError(f"'{tokens[0]!r}' tag doesn't receive any arguments.")
    renderer = apps.get_app_config(MJMLConfig.name).get_renderer()
    return MJMLRenderNode(nodelist, renderer=renderer)
