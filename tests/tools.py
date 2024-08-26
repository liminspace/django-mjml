import copy
import os
import subprocess
import time
from contextlib import contextmanager, suppress
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from django.conf import settings
from django.template import Context, Template

from mjml import settings as mjml_settings


def get_mjml_version() -> int:
    env_ver = os.environ.get("MJML_VERSION", None)
    if env_ver:
        with suppress(ValueError, TypeError, IndexError):
            return int(env_ver.split(".")[0])

    return settings.DEFAULT_MJML_VERSION


@contextmanager
def safe_change_mjml_settings():
    """
    with safe_change_mjml_settings() as mjml_app_config:
        mjml_settins.MJML_EXEC_PATH = 'other value'
        mjml_app_config.ready()
        ...
    # mjml settings will be restored
    ...
    """
    from django.apps import apps

    settings_bak = {}
    for k, v in mjml_settings.__dict__.items():
        if k[:5] == "MJML_":
            settings_bak[k] = copy.deepcopy(v)
    mjml_app_config = apps.get_app_config("mjml")
    try:
        yield mjml_app_config
    finally:
        for k, v in settings_bak.items():
            setattr(mjml_settings, k, v)
        mjml_app_config.ready()


def render_tpl(tpl: str, context: Optional[Dict[str, Any]] = None) -> str:
    if get_mjml_version() >= 4:
        tpl = tpl.replace("<mj-container>", "").replace("</mj-container>", "")
    return Template("{% load mjml %}" + tpl).render(Context(context))


class MJMLServers:
    SERVER_TYPE: str  # tcpserver, httpserver
    _processes: List[subprocess.Popen] = []

    @classmethod
    def _terminate_processes(cls) -> None:
        while cls._processes:
            p = cls._processes.pop()
            p.terminate()

    @classmethod
    def _start_tcp_servers(cls) -> None:
        root_dir = settings.BASE_DIR.parent
        tcpserver_path = root_dir / "mjml-tcpserver/tcpserver.js"
        env = os.environ.copy()
        env["NODE_PATH"] = root_dir
        for host, port in mjml_settings.MJML_TCPSERVERS:  # type: ignore  # TODO: fix
            p = subprocess.Popen(
                [
                    "node",
                    tcpserver_path,
                    f"--port={port}",
                    f"--host={host}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def _stop_tcp_servers(cls) -> None:
        cls._terminate_processes()

    @classmethod
    def _start_http_servers(cls) -> None:
        env = os.environ.copy()
        for server_conf in mjml_settings.MJML_HTTPSERVERS:  # type: ignore  # TODO: fix
            parsed = urlparse(server_conf["URL"])
            host, port = parsed.netloc.split(":")
            p = subprocess.Popen(
                [
                    "mjml-http-server",
                    f"--host={host}",
                    f"--port={port}",
                    "--max-body=8500kb",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            cls._processes.append(p)
        time.sleep(5)

    @classmethod
    def _stop_http_servers(cls) -> None:
        cls._terminate_processes()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()  # type: ignore
        if cls.SERVER_TYPE == "tcpserver":
            cls._start_tcp_servers()
        elif cls.SERVER_TYPE == "httpserver":
            cls._start_http_servers()
        else:
            err_msg = f"Invalid SERVER_TYPE: {cls.SERVER_TYPE}"
            raise RuntimeError(err_msg)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.SERVER_TYPE == "tcpserver":
            cls._stop_tcp_servers()
        elif cls.SERVER_TYPE == "httpserver":
            cls._stop_http_servers()
        else:
            err_msg = f"Invalid SERVER_TYPE: {cls.SERVER_TYPE}"
            raise RuntimeError(err_msg)
        super().tearDownClass()  # type: ignore


class MJMLFixtures:
    TPLS = {
        "simple": """
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-image src="img/test.png"></mj-image>
                            <mj-text font-size="20px" align="center">Test title</mj-text>
                        </mj-column>
                    </mj-section>
                    <mj-section>
                        <mj-column>
                            <mj-button background-color="#ffcc00" font-size="15px">Test button</mj-button>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
        "with_text_context": """
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-text>{{ text }}</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
        "with_text_context_and_unicode": """
            {% mjml %}
                <mjml>
                <mj-body>
                <mj-container>
                    <mj-section>
                        <mj-column>
                            <mj-text>Український текст {{ text }} ©</mj-text>
                        </mj-column>
                    </mj-section>
                </mj-container>
                </mj-body>
                </mjml>
            {% endmjml %}
        """,
    }
    SYMBOLS = {
        "smile": "\u263a",
        "checkmark": "\u2713",
        "candy": "\U0001f36d",  # b'\xf0\x9f\x8d\xad'.decode('utf-8')
    }
    TEXTS = {
        "unicode": SYMBOLS["smile"] + SYMBOLS["checkmark"] + SYMBOLS["candy"],
    }
