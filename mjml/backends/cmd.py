import subprocess
import tempfile
from copy import copy
from typing import Any, Dict, List, Optional

from django.utils.encoding import force_bytes, force_str

from mjml.backends.base import BaseRendererBackend
from mjml.backends.exceptions import RendererBackendCheckFailedError


class CMDBackend(BaseRendererBackend):
    def __init__(
        self,
        cmd_args: List[str],
        cmd_env_vars: Optional[Dict[str, str]] = None,
        check_on_startup: bool = True,
    ) -> None:
        self._cmd_args = cmd_args
        self._cmd_env_vars = cmd_env_vars
        self._check_on_startup = check_on_startup

    @classmethod
    def create(cls, params: Dict[str, Any]) -> BaseRendererBackend:
        cmd_args = cls._parse_raw_cmd_args_param(raw_cmd_args_param=params["CMD_ARGS"])
        cmd_env_vars = copy(params.get("CMD_ENV_VARS"))
        check_on_startup = params.get("CHECK_ON_STARTUP", True)
        return cls(
            cmd_args=cmd_args,
            cmd_env_vars=cmd_env_vars,
            check_on_startup=check_on_startup,
        )

    @classmethod
    def _parse_raw_cmd_args_param(cls, raw_cmd_args_param: Any) -> List[str]:
        cmd_args_param = copy(raw_cmd_args_param)
        if isinstance(cmd_args_param, tuple):
            cmd_args_param = list(cmd_args_param)
        elif not isinstance(cmd_args_param, list):
            cmd_args_param = [cmd_args_param]

        for ca in ("-i", "-s"):
            if ca not in cmd_args_param:
                cmd_args_param.append(ca)

        return cmd_args_param

    def render_mjml_to_html(self, mjml_source: str) -> str:
        with tempfile.SpooledTemporaryFile(max_size=(5 * 1024 * 1024)) as stdout_tmp_f:
            try:
                p = subprocess.Popen(
                    self._cmd_args,
                    stdin=subprocess.PIPE,
                    stdout=stdout_tmp_f,
                    stderr=subprocess.PIPE,
                    env=self._cmd_env_vars,
                )
                stderr = p.communicate(force_bytes(mjml_source))[1]
            except OSError as e:
                cmd_str = " ".join(self._cmd_args)
                raise RuntimeError(
                    f'Problem to run command "{cmd_str}"\n'
                    f"{e}\n"
                    "Check that mjml is installed and allow permissions to execute.\n"
                    "See https://github.com/mjmlio/mjml#installation"
                ) from e
            stdout_tmp_f.seek(0)
            stdout = stdout_tmp_f.read()

        if stderr:
            raise RuntimeError(f"MJML stderr is not empty: {force_str(stderr)}.")

        return force_str(stdout)

    def check(self) -> None:
        if not self._check_on_startup:
            return None

        try:
            html = self.render_mjml_to_html(
                "<mjml><mj-body><mj-container><mj-text>" "MJMLv3" "</mj-text></mj-container></mj-body></mjml>"
            )
        except RuntimeError:
            try:
                html = self.render_mjml_to_html(
                    "<mjml><mj-body><mj-section><mj-column><mj-text>"
                    "MJMLv4"
                    "</mj-text></mj-column></mj-section></mj-body></mjml>"
                )
            except RuntimeError as e:
                raise RendererBackendCheckFailedError(e) from e
        if "<html " not in html:
            raise RendererBackendCheckFailedError(
                "mjml command returns wrong result.\n"
                "Check MJML is installed correctly. See https://github.com/mjmlio/mjml#installation"
            )
