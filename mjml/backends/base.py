from typing import Any, Dict


class BaseRendererBackend:
    def render_mjml_to_html(self, mjml_source: str) -> str:
        raise NotImplementedError

    @classmethod
    def create(cls, params: Dict[str, Any]) -> "BaseRendererBackend":
        raise NotImplementedError

    def check(self) -> None:
        return None
