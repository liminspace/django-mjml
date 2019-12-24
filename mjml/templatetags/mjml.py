from __future__ import absolute_import
from django import template
from mjml.tools import mjml_render


register = template.Library()


class MJMLRenderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        mjml = self.nodelist.render(context)
        return mjml_render(mjml)


@register.tag
def mjml(parser, token):
    """
    Compile MJML template after render django template.

    Usage:
        {% mjml %}
            .. MJML template code ..
        {% endmjml %}
    """
    nodelist = parser.parse(('endmjml',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) != 1:
        raise template.TemplateSyntaxError("'%r' tag doesn't receive any arguments." % tokens[0])
    return MJMLRenderNode(nodelist)
