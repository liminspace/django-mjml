import json
import random
from typing import Dict, List, Optional

from django.utils.encoding import force_bytes, force_str

from .base import BaseBackend


class HttpBackend(BaseBackend):
    """
    Render MJML templates through an HTTP call to a server
    that renders the MJML and returns the result
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.servers = self.options.get("servers", [])

    def render(self, mjml_code: str) -> str:
        import requests.auth

        if len(self.servers) > 1:
            random.shuffle(self.servers)

        timeouts = 0
        for server in self.servers:
            auth = (
                requests.auth.HTTPBasicAuth(*server["auth"])
                if server.get("auth")
                else None
            )

            try:
                response = requests.post(
                    url=server["url"],
                    auth=auth,
                    data=force_bytes(json.dumps({"mjml": mjml_code})),
                    headers={"Content-Type": "application/json"},
                    timeout=25,
                )
            except requests.exceptions.Timeout:
                timeouts += 1
                continue

            try:
                data = response.json()
            except (TypeError, json.JSONDecodeError):
                data = {}

            if response.status_code == 200:
                errors: Optional[List[Dict]] = data.get("errors")
                if errors:
                    msg_lines = [
                        f"Line: {e.get('line')} Tag: {e.get('tagName')} Message: {e.get('message')}"
                        for e in errors
                    ]
                    msg_str = "\n".join(msg_lines)
                    raise RuntimeError(
                        f"MJML compile error (via MJML HTTP server): {msg_str}"
                    )

                return force_str(data["html"])
            else:
                msg = (
                    f"[code={response.status_code}, request_id={data.get('request_id', '')}] "
                    f"{data.get('message', 'Unknown error.')}"
                )
                raise RuntimeError(f"MJML compile error (via MJML HTTP server): {msg}")

        raise RuntimeError(
            "MJML compile error (via MJML HTTP server): no working server\n"
            f"Number of servers: {len(self.servers)}\n"
            f"Timeouts: {timeouts}"
        )
