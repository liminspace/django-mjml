import subprocess
from django import template
from ..tools import get_mjml_popen_args


register = template.Library()


class MJMLRenderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        mjml = self.nodelist.render(context)
        p = subprocess.Popen(get_mjml_popen_args(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        html = p.communicate(mjml)[0]
        return html


@register.tag
def mjml(parser, token):
    """
    Compile MJML template every time.

    Usage::
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


# todo add tag mjml_cacheble
