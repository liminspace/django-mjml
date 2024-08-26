import json
import random
from typing import Any, Dict, List, Optional, Tuple, Union

import requests.auth
from django.utils.encoding import force_bytes, force_str

from mjml.backends.base import BaseRendererBackend


class RequestsHTTPServerBackend(BaseRendererBackend):
    _AUTH_TYPES: Dict[str, Any] = {"BASIC": requests.auth.HTTPBasicAuth}

    def __init__(self, servers_params: List[Dict]) -> None:
        self._servers_params: List[Dict] = servers_params

    @classmethod
    def create(cls, params: Dict[str, Any]) -> BaseRendererBackend:
        servers_params: List[Dict] = [
            cls._parse_raw_server_params(raw_server_params=raw_server_params)
            for raw_server_params in params["SERVERS"]
        ]
        return cls(servers_params=servers_params)

    @classmethod
    def _parse_raw_server_params(cls, raw_server_params: Dict[str, Any]) -> Dict[str, Any]:
        server_params = {
            "auth": None,
            "url": raw_server_params["URL"],
        }

        auth_raw = raw_server_params.get("AUTH")
        if auth_raw:
            if isinstance(auth_raw, (list, tuple)) and len(auth_raw) == 2:
                if isinstance(auth_raw[1], (list, tuple)):
                    auth_type, auth_params = auth_raw[0], auth_raw[1]
                else:
                    auth_type, auth_params = "BASIC", auth_raw
            else:
                err_msg = "Invalid AUTH value"
                raise ValueError(err_msg)

            server_params["auth"] = cls._get_auth_instance(
                auth_type=auth_type,
                auth_params=auth_params,
            )

        return server_params

    def _get_server_ixs(self) -> List[int]:
        ixs = list(range(len(self._servers_params)))
        random.shuffle(ixs)
        return ixs

    @classmethod
    def _get_auth_instance(cls, auth_type: str, auth_params: Union[List, Tuple, Dict]):
        auth_cls = cls._AUTH_TYPES[auth_type]
        if isinstance(auth_params, dict):
            instance = auth_cls(**auth_params)
        elif isinstance(auth_params, (list, tuple)):
            instance = auth_cls(*auth_params)
        else:
            err_msg = "Invalid type of auth_params"
            raise ValueError(err_msg)
        return instance

    def render_mjml_to_html(self, mjml_source: str) -> str:
        timeouts = 0
        for server_ix in self._get_server_ixs():
            server_params = self._servers_params[server_ix]
            auth = server_params["auth"]
            try:
                response = requests.post(
                    url=server_params["url"],
                    auth=auth,
                    data=force_bytes(json.dumps({"mjml": mjml_source})),
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
                        f'Line: {e.get("line")} Tag: {e.get("tagName")} Message: {e.get("message")}' for e in errors
                    ]
                    msg_str = "\n".join(msg_lines)
                    err_msg = f"MJML compile error (via MJML HTTP server): {msg_str}"
                    raise RuntimeError(err_msg)

                return force_str(data["html"])
            msg = (
                f"[code={response.status_code}, request_id={data.get('request_id', '')}] "
                f"{data.get('message', 'Unknown error.')}"
            )
            err_msg = f"MJML compile error (via MJML HTTP server): {msg}"
            raise RuntimeError(err_msg)

        err_msg = (
            "MJML compile error (via MJML HTTP server): no working server\n"
            f"Number of servers: {len(self._servers_params)}\n"
            f"Timeouts: {timeouts}"
        )
        raise RuntimeError(err_msg)
