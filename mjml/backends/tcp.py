import random
import socket
from typing import Any, Dict, List, Optional, Tuple, Union

from django.utils.encoding import force_bytes, force_str

from mjml.backends.base import BaseRendererBackend


class TCPServerBackend(BaseRendererBackend):
    def __init__(self, servers_params: List[Tuple[str, int]]) -> None:
        self._servers_params: List[Tuple[str, int]] = servers_params

    @classmethod
    def create(cls, params: Dict[str, Any]) -> BaseRendererBackend:
        servers_params = [
            cls._parse_raw_server_params(raw_server_params=raw_server_params)
            for raw_server_params in params["SERVERS"]
        ]
        return cls(servers_params=servers_params)

    @classmethod
    def _parse_raw_server_params(cls, raw_server_params: Union[List, Tuple]) -> Tuple[str, int]:
        host, port = raw_server_params
        if isinstance(port, str):
            port = int(port)

        return host, port

    def _get_server_ixs(self) -> List[int]:
        ixs = list(range(len(self._servers_params)))
        random.shuffle(ixs)
        return ixs

    def render_mjml_to_html(self, mjml_source: str) -> str:
        mjml_source_data = force_bytes(mjml_source)
        mjml_source_data = force_bytes(f"{len(mjml_source_data):09d}") + mjml_source_data
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.settimeout(25)
        timeouts = 0
        for server_ix in self._get_server_ixs():
            host, port = self._servers_params[server_ix]
            try:
                s.connect((host, port))
            except socket.timeout:
                timeouts += 1
                continue
            except OSError:
                continue
            try:
                s.sendall(mjml_source_data)
                ok = force_str(self._socket_recvall(s, 1)) == "0"
                a = force_str(self._socket_recvall(s, 9))
                result_len = int(a)
                result = force_str(self._socket_recvall(s, result_len))
                if ok:
                    return result
                else:
                    raise RuntimeError(f"MJML compile error (via MJML TCP server): {result}")
            except socket.timeout:
                timeouts += 1
            finally:
                s.close()
        raise RuntimeError(
            "MJML compile error (via MJML TCP server): no working server\n"
            f"Number of servers: {len(self._servers_params)}\n"
            f"Timeouts: {timeouts}"
        )

    @classmethod
    def _socket_recvall(cls, sock: socket.socket, n: int) -> Optional[bytes]:
        data = b""
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data
