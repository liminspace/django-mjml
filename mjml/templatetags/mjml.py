from django import template
from django.core.cache import InvalidCacheBackendError, caches
from ..tools import mjml_render, make_mjml_fragment_key


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


class MJMLCachebleRenderNode(template.Node):
    def __init__(self, mjml_tpl, expire_time_var, fragment_name, use_cache_var):
        self.mjml_tpl = mjml_tpl
        self.expire_time_var = expire_time_var
        self.fragment_name = fragment_name
        self.use_cache_var = use_cache_var

    def render(self, context):
        use_cache_val = None if self.use_cache_var is None else self.use_cache_var.resolve(context)
        try:
            cache = caches['default' if use_cache_val is None else use_cache_val]
        except InvalidCacheBackendError:
            raise template.TemplateSyntaxError(
                'Invalid cache name specified for mjml_cacheble tag: %r' % use_cache_val
            )
        expire_time_val = self.expire_time_var.resolve(context)
        try:
            expire_time = int(expire_time_val)
        except (template.VariableDoesNotExist, ValueError, TypeError):
            raise template.TemplateSyntaxError(
                '"mjml_cacheble" tag got a non-integer timeout value: %r' % expire_time_val
            )
        key = make_mjml_fragment_key(self.fragment_name)
        tpl = cache.get(key)
        if tpl is None:
            tpl = mjml_render(self.mjml_tpl)
            if expire_time > 0:
                cache.set(key, tpl, expire_time)
        t = template.Template(tpl)
        return t.render(context)


@register.tag
def mjml_cacheble(parser, token):
    """
    Compile MJML template before render django template.
    It is possible to cache compiled result for faster work.

    Usage with caching:
        {% mjml_cacheble [expire_time] [fragment_name] %}
            .. MJML template code ..
        {% endmjml %}

    Set expire_time to 0 for disable caching.

    You can use other cache:
        {% mjml_cacheble [expire_time] [fragment_name] use_cache='cachename' %}
    """
    tokens = token.split_contents()
    use_cache = None
    if len(tokens) < 3:
        raise template.TemplateSyntaxError("'%r' tag requires at least 2 arguments." % tokens[0])
    elif len(tokens) > 4:
        raise template.TemplateSyntaxError("'%r' tag can receive up to 3 arguments." % tokens[0])
    elif len(tokens) == 4:
        use_cache = tokens[-1]
        if not use_cache.startswith('use_cache='):
            raise template.TemplateSyntaxError(("'%r' receive invalid last argument. "
                                                "Use use_cache='cachename' for fourth argument.") % tokens[0])
        use_cache = parser.compile_filter(use_cache[len('use_cache='):])
        tokens = tokens[:-1]
    mjml_pieces = []
    parse_until = 'endmjml_cacheble'
    tag_mapping = {
        template.base.TOKEN_VAR: ('{{ ', ' }}'),
        template.base.TOKEN_BLOCK: ('{% ', ' %}'),
    }
    while parser.tokens:
        tok = parser.next_token()
        if tok.token_type == template.base.TOKEN_COMMENT:
            continue
        elif tok.token_type == template.base.TOKEN_TEXT:
            mjml_pieces.append(tok.contents)
        else:
            if tok.token_type == template.base.TOKEN_BLOCK and tok.contents == parse_until:
                break
            tag = '{1}{0}{2}'.format(tok.contents, *tag_mapping[tok.token_type])
            mjml_pieces.append('<mj-raw>{}</mj-raw>'.format(tag))
    else:
        parser.unclosed_block_tag(parse_until)
    return MJMLCachebleRenderNode(''.join(mjml_pieces), parser.compile_filter(tokens[1]), tokens[2], use_cache)
