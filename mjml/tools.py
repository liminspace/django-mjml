import copy
import json
import random
import socket
import subprocess
import tempfile
from typing import Optional, Dict, List

from django.utils.encoding import force_str, force_bytes

from mjml import settings as mjml_settings

_cache = {}


def _mjml_render_by_cmd(mjml_code: str) -> str:
    if 'cmd_args' not in _cache:
        cmd_args = copy.copy(mjml_settings.MJML_EXEC_CMD)
        if not isinstance(cmd_args, list):
            cmd_args = [cmd_args]
        for ca in ('-i', '-s'):
            if ca not in cmd_args:
                cmd_args.append(ca)
        _cache['cmd_args'] = cmd_args
    else:
        cmd_args = _cache['cmd_args']

    with tempfile.SpooledTemporaryFile(max_size=(5 * 1024 * 1024)) as stdout_tmp_f:
        try:
            p = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=stdout_tmp_f, stderr=subprocess.PIPE)
            stderr = p.communicate(force_bytes(mjml_code))[1]
        except (IOError, OSError) as e:
            cmd_str = ' '.join(cmd_args)
            raise RuntimeError(
                f'Problem to run command "{cmd_str}"\n'
                f'{e}\n'
                'Check that mjml is installed and allow permissions to execute.\n'
                'See https://github.com/mjmlio/mjml#installation'
            ) from e
        stdout_tmp_f.seek(0)
        stdout = stdout_tmp_f.read()

    if stderr:
        raise RuntimeError(f'MJML stderr is not empty: {force_str(stderr)}.')

    return force_str(stdout)


def socket_recvall(sock: socket.socket, n: int) -> Optional[bytes]:
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return
        data += packet
    return data


def _mjml_render_by_tcpserver(mjml_code: str) -> str:
    if len(mjml_settings.MJML_TCPSERVERS) > 1:
        servers = list(mjml_settings.MJML_TCPSERVERS)[:]
        random.shuffle(servers)
    else:
        servers = mjml_settings.MJML_TCPSERVERS
    mjml_code_data = force_bytes(mjml_code)
    mjml_code_data = force_bytes('{:09d}'.format(len(mjml_code_data))) + mjml_code_data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.settimeout(25)
    timeouts = 0
    for host, port in servers:
        try:
            s.connect((host, port))
        except socket.timeout:
            timeouts += 1
            continue
        except socket.error:
            continue
        try:
            s.sendall(mjml_code_data)
            ok = force_str(socket_recvall(s, 1)) == '0'
            a = force_str(socket_recvall(s, 9))
            result_len = int(a)
            result = force_str(socket_recvall(s, result_len))
            if ok:
                return result
            else:
                raise RuntimeError(f'MJML compile error (via MJML TCP server): {result}')
        except socket.timeout:
            timeouts += 1
        finally:
            s.close()
    raise RuntimeError(
        'MJML compile error (via MJML TCP server): no working server\n'
        f'Number of servers: {len(servers)}\n'
        f'Timeouts: {timeouts}'
    )


def _mjml_render_by_httpserver(mjml_code: str) -> str:
    import requests.auth

    if len(mjml_settings.MJML_HTTPSERVERS) > 1:
        servers = list(mjml_settings.MJML_HTTPSERVERS)[:]
        random.shuffle(servers)
    else:
        servers = mjml_settings.MJML_HTTPSERVERS

    timeouts = 0
    for server_conf in servers:
        http_auth = server_conf.get('HTTP_AUTH')
        auth = requests.auth.HTTPBasicAuth(*http_auth) if http_auth else None

        try:
            response = requests.post(
                url=server_conf['URL'],
                auth=auth,
                data=force_bytes(json.dumps({'mjml': mjml_code})),
                headers={'Content-Type': 'application/json'},
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
            errors: Optional[List[Dict]] = data.get('errors')
            if errors:
                msg_lines = [
                    f'Line: {e.get("line")} Tag: {e.get("tagName")} Message: {e.get("message")}'
                    for e in errors
                ]
                msg_str = '\n'.join(msg_lines)
                raise RuntimeError(f'MJML compile error (via MJML HTTP server): {msg_str}')

            return force_str(data['html'])
        else:
            msg = (
                f"[code={response.status_code}, request_id={data.get('request_id', '')}] "
                f"{data.get('message', 'Unknown error.')}"
            )
            raise RuntimeError(f'MJML compile error (via MJML HTTP server): {msg}')

    raise RuntimeError(
        'MJML compile error (via MJML HTTP server): no working server\n'
        f'Number of servers: {len(servers)}\n'
        f'Timeouts: {timeouts}'
    )


def mjml_render(mjml_source: str) -> str:
    if mjml_settings.MJML_BACKEND_MODE == 'cmd':
        return _mjml_render_by_cmd(mjml_source)
    elif mjml_settings.MJML_BACKEND_MODE == 'tcpserver':
        return _mjml_render_by_tcpserver(mjml_source)
    elif mjml_settings.MJML_BACKEND_MODE == 'httpserver':
        return _mjml_render_by_httpserver(mjml_source)
    raise RuntimeError(f'Invalid settings.MJML_BACKEND_MODE "{mjml_settings.MJML_BACKEND_MODE}"')
