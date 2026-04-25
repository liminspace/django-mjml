from mjml.backend import default_mjml_backend


def mjml_render(mjml_source: str) -> str:
    return default_mjml_backend.render(mjml_source)
