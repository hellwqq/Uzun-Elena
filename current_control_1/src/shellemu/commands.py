"""Built-in commands of the emulator."""
from .config import UNSET
from .errors import ShellError

EXIT_CODE_MODULO = 256


def _stub(name, args):
    """Return the text printed by a placeholder command."""
    return f"{name} {args}"


def cmd_ls(shell, args):
    """Placeholder for ls: print its name and arguments."""
    return _stub("ls", args)


def cmd_cd(shell, args):
    """Placeholder for cd: print its name and arguments."""
    return _stub("cd", args)


def _parse_code(text):
    """Convert the argument of exit to a process exit code."""
    try:
        return int(text) % EXIT_CODE_MODULO
    except ValueError as err:
        raise ShellError("exit: numeric argument required") from err


def cmd_exit(shell, args):
    """Stop the shell, optionally with a numeric exit code."""
    if len(args) > 1:
        raise ShellError("exit: too many arguments")
    if args:
        shell.exit_code = _parse_code(args[0])
    shell.running = False
    return ""


def cmd_conf_dump(shell, args):
    """Print emulator parameters as key=value lines."""
    if args:
        raise ShellError("conf-dump: too many arguments")
    return shell.config.dump()


def cmd_vfs_info(shell, args):
    """Print the source and the size of the loaded VFS."""
    if args:
        raise ShellError("vfs-info: too many arguments")
    dirs, files, size = shell.vfs.stats()
    return "\n".join([
        f"source={shell.vfs.source or UNSET}",
        f"directories={dirs}",
        f"files={files}",
        f"bytes={size}",
    ])


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "conf-dump": cmd_conf_dump,
    "vfs-info": cmd_vfs_info,
}
