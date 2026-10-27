"""Command line interface of the emulator."""
import sys

from .config import parse_args
from .errors import ShellError
from .shell import Shell
from .vfs import Vfs

EXIT_FAILURE = 1


def _use_utf8():
    """Make standard streams print and read UTF-8 on any platform."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def print_debug(config):
    """Show all configured parameters at the start of the emulator."""
    print("[debug] emulator parameters:")
    for key, value in config.items():
        print(f"[debug]   {key}={value}")


def main(argv=None):
    """Start the emulator and return the process exit code."""
    _use_utf8()
    config = parse_args(argv)
    print_debug(config)
    shell = Shell(config)
    try:
        if config.vfs_path:
            shell.vfs = Vfs.from_zip(config.vfs_path)
        if config.script_path:
            shell.run_script(config.script_path)
    except ShellError as err:
        print(err, file=sys.stderr)
        return EXIT_FAILURE
    if shell.running:
        shell.run_repl()
    return shell.exit_code
