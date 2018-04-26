import copy
import socket
import random
import subprocess
from django.utils.encoding import force_str
from . import settings as mjml_settings


_cache = {}


def _mjml_render_by_cmd(mjml_code):
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

    try:
        p = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(mjml_code.encode('utf8'))
    except (IOError, OSError) as e:
        raise RuntimeError(
            'Problem to run command "{}"\n'.format(' '.join(cmd_args)) +
            '{}\n'.format(e) +
            'Check that mjml is installed and allow permissions for execute.\n' +
            'See https://github.com/mjmlio/mjml#installation'
        )
    if stderr:
        raise RuntimeError('MJML stderr is not empty: {}.'.format(force_str(stderr)))

    return force_str(stdout)


def socket_recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return
        data += packet
    return data


def _mjml_render_by_tcpserver(mjml_code):
    if len(mjml_settings.MJML_TCPSERVERS) > 1:
        servers = list(mjml_settings.MJML_TCPSERVERS)[:]
        random.shuffle(servers)
    else:
        servers = mjml_settings.MJML_TCPSERVERS

    mjml_code = mjml_code.encode('utf8') or ' '
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
            s.sendall('{:09d}'.format(len(mjml_code.decode('utf8'))).encode('utf8'))
            s.sendall(mjml_code)
            ok = force_str(socket_recvall(s, 1)) == '0'
            a = force_str(socket_recvall(s, 9))
            result_len = int(a)
            result = force_str(socket_recvall(s, result_len))
            if ok:
                return result
            else:
                raise RuntimeError('MJML compile error (via MJML TCP server): {}'.format(result))
        except socket.timeout:
            timeouts += 1
        finally:
            s.close()
    raise RuntimeError(
        ('MJML compile error (via MJML TCP server): no working server\n'
         'Number of servers: {total}\n'
         'Timeouts: {timeouts}').format(total=len(servers), timeouts=timeouts)
    )


def mjml_render(mjml_code):
    if mjml_code is '':
        return mjml_code

    if mjml_settings.MJML_BACKEND_MODE == 'cmd':
        return _mjml_render_by_cmd(mjml_code)
    elif mjml_settings.MJML_BACKEND_MODE == 'tcpserver':
        return _mjml_render_by_tcpserver(mjml_code)
    raise RuntimeError('Invalid settings.MJML_BACKEND_MODE "{}"'.format(mjml_settings.MJML_BACKEND_MODE))
