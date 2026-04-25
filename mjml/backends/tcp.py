import random
import socket
from typing import Optional

from django.utils.encoding import force_bytes, force_str

from .base import BaseBackend


class TcpBackend(BaseBackend):
    """
    Render MJML templates through an TCP call to a server
    that renders the MJML and returns the result
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.servers = self.options.get("servers", [])

    def _socket_recvall(self, sock: socket.socket, n: int) -> Optional[bytes]:
        data = b""
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return
            data += packet
        return data

    def render(self, mjml_code: str) -> str:

        if len(self.servers) > 1:
            random.shuffle(self.servers)

        mjml_code_data = force_bytes(mjml_code)
        mjml_code_data = (
            force_bytes("{:09d}".format(len(mjml_code_data))) + mjml_code_data
        )
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.settimeout(25)
        timeouts = 0
        for host, port in self.servers:
            try:
                s.connect((host, port))
            except socket.timeout:
                timeouts += 1
                continue
            except socket.error:
                continue
            try:
                s.sendall(mjml_code_data)
                ok = force_str(self._socket_recvall(s, 1)) == "0"
                a = force_str(self._socket_recvall(s, 9))
                result_len = int(a)
                result = force_str(self._socket_recvall(s, result_len))
                if ok:
                    return result
                else:
                    raise RuntimeError(
                        f"MJML compile error (via MJML TCP server): {result}"
                    )
            except socket.timeout:
                timeouts += 1
            finally:
                s.close()
        raise RuntimeError(
            "MJML compile error (via MJML TCP server): no working server\n"
            f"Number of servers: {len(self.servers)}\n"
            f"Timeouts: {timeouts}"
        )
