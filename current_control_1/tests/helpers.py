"""Helpers shared by the tests."""
import io
import zipfile

from shellemu.shell import Shell
from shellemu.vfs import Vfs

MODE_SHIFT = 16
DOS_ARCHIVE_FLAG = 0x20


def build_zip(entries):
    """Create ZIP bytes from (name, data, mode) tuples.

    A mode of None mimics an archive made on DOS without UNIX modes.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data, mode in entries:
            info = zipfile.ZipInfo(name)
            info.external_attr = DOS_ARCHIVE_FLAG
            if mode is not None:
                info.external_attr = mode << MODE_SHIFT
            archive.writestr(info, data)
    return buffer.getvalue()


def make_shell(entries=None):
    """Create a shell with an in-memory output and an optional VFS."""
    shell = Shell(out=io.StringIO())
    if entries is not None:
        shell.vfs = Vfs.from_bytes(build_zip(entries))
    return shell


def run(shell, line):
    """Execute one line and return everything it printed."""
    shell.out.seek(0)
    shell.out.truncate()
    shell.execute(line)
    return shell.out.getvalue().rstrip("\n")
