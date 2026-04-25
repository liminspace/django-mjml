from abc import ABC, abstractmethod

from django.core.exceptions import ImproperlyConfigured


class BaseBackend(ABC):
    """
    Base class for the MJML Backend
    The key function of the backend is to take mjml content and
    render it as HTML
    Each backend must implement the render function which performs this task
    and is called by the template tag
    """

    check_on_startup: bool = False

    def __init__(self, alias: str, params: dict):
        self.alias = alias
        self.options = params.get("OPTIONS", {})

        if "check_on_startup" in self.options:
            self.check_on_startup = self.options["check_on_startup"]

    @abstractmethod
    def render(self, mjml_code: str) -> str:
        """
        Given the mjml code from a template, render this
        using mjml and return the rendered result
        """

        raise NotImplementedError

    def check(self):
        try:
            html = self.render(
                "<mjml><mj-body><mj-section><mj-column><mj-text>"
                "MJMLv4"
                "</mj-text></mj-column></mj-section></mj-body></mjml>"
            )
        except RuntimeError as e:
            raise ImproperlyConfigured(e) from e

        if "<html " not in html:
            raise ImproperlyConfigured(
                "mjml command returns wrong result.\n"
                "Check MJML is installed correctly. See https://github.com/mjmlio/mjml#installation"
            )

        return html
