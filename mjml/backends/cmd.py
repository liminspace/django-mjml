import subprocess
import tempfile

from django.utils.encoding import force_bytes, force_str

from .base import BaseBackend


class CmdBackend(BaseBackend):
    """
    A backend which uses subprocess to invoke an command that
    Takes the mjml_code via stdin
    Returns the html as stdout
    """

    exec_cmd: str | list[str] = ["mjml"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "exec_cmd" in self.options:
            self.exec_cmd = self.options["exec_cmd"]

        if not isinstance(self.exec_cmd, list):
            self.exec_cmd = [self.exec_cmd]

        for ca in ("-i", "-s"):
            if ca not in self.exec_cmd:
                self.exec_cmd.append(ca)

    def render(self, mjml_code: str) -> str:

        with (
            tempfile.SpooledTemporaryFile(max_size=(5 * 1024 * 1024)) as stdout_tmp_f,
            tempfile.SpooledTemporaryFile(max_size=(5 * 1024 * 1024)) as stdin_tmp_f,
        ):
            stdin_tmp_f.write(force_bytes(mjml_code))
            stdin_tmp_f.seek(0)

            try:
                p = subprocess.run(
                    self.exec_cmd,
                    stdin=stdin_tmp_f,
                    stdout=stdout_tmp_f,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=False,
                )

            except FileNotFoundError as e:
                raise RuntimeError(
                    f"Could not find the path to the mjml executable {e.filename}\n"
                    "See https://github.com/mjmlio/mjml#installation"
                ) from e

            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    f'There was a problem running command "{e.cmd}"\n'
                    f"{force_str(e.stderr)}\n"
                    "Check that mjml is installed and allow permissions to execute.\n"
                    "See https://github.com/mjmlio/mjml#installation"
                ) from e

            stdout_tmp_f.seek(0)
            stdout = stdout_tmp_f.read()

            if p.stderr:
                raise RuntimeError(f"MJML stderr is not empty: {force_str(p.stderr)}.")

            return force_str(stdout)
