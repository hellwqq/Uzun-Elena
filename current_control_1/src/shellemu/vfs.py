"""In-memory virtual file system backed by a ZIP archive."""
import io
import zipfile
from dataclasses import dataclass, field

from .errors import ShellError

DEFAULT_DIR_MODE = 0o755
DEFAULT_FILE_MODE = 0o644
MODE_MASK = 0o777
UNIX_MODE_SHIFT = 16
SEPARATOR = "/"
IGNORED_PIECES = ("", ".")
PARENT = ".."


@dataclass
class Node:
    """A file or a directory of the virtual file system."""

    name: str
    is_dir: bool
    mode: int
    data: bytes = b""
    children: dict = field(default_factory=dict)


def split_member_name(name):
    """Split an archive member name into safe path components."""
    parts = []
    for piece in name.split(SEPARATOR):
        if piece == PARENT:
            raise ShellError(f"vfs: unsafe path in archive: {name}")
        if piece not in IGNORED_PIECES:
            parts.append(piece)
    return parts


def member_mode(info):
    """Return permission bits stored in an archive member."""
    stored = (info.external_attr >> UNIX_MODE_SHIFT) & MODE_MASK
    if stored:
        return stored
    return DEFAULT_DIR_MODE if info.is_dir() else DEFAULT_FILE_MODE


def count_nodes(node):
    """Count directories and files below a node (the node excluded)."""
    dirs = files = 0
    for child in node.children.values():
        if child.is_dir:
            sub_dirs, sub_files = count_nodes(child)
            dirs += 1 + sub_dirs
            files += sub_files
        else:
            files += 1
    return dirs, files


def total_size(node):
    """Return the number of data bytes stored below a node."""
    size = len(node.data)
    for child in node.children.values():
        size += total_size(child)
    return size


class Vfs:
    """Tree of nodes kept entirely in memory."""

    def __init__(self, source=""):
        """Create an empty file system remembering where it came from."""
        self.root = Node("", True, DEFAULT_DIR_MODE)
        self.source = source

    @classmethod
    def from_zip(cls, path):
        """Load a file system from the ZIP archive stored at path."""
        try:
            with open(path, "rb") as handle:
                raw = handle.read()
        except OSError as err:
            raise ShellError(
                f"vfs: cannot read '{path}': {err.strerror}"
            ) from err
        return cls.from_bytes(raw, path)

    @classmethod
    def from_bytes(cls, raw, source=""):
        """Build a file system from the bytes of a ZIP archive."""
        vfs = cls(source)
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                for info in archive.infolist():
                    vfs.add_member(info, archive.read(info))
        except (zipfile.BadZipFile, NotImplementedError, RuntimeError) as err:
            raise ShellError(
                f"vfs: '{source}' is not a readable ZIP archive: {err}"
            ) from err
        return vfs

    def ensure_dir(self, parts, final_mode=None):
        """Return the directory at parts, creating missing ones."""
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = Node(part, True, DEFAULT_DIR_MODE)
                node.children[part] = child
            elif not child.is_dir:
                raise ShellError(f"vfs: '{part}' is a file and a directory")
            node = child
        if final_mode is not None:
            node.mode = final_mode
        return node

    def add_member(self, info, data):
        """Add one archive member (file or directory) to the tree."""
        parts = split_member_name(info.filename)
        if not parts:
            return
        mode = member_mode(info)
        if info.is_dir():
            self.ensure_dir(parts, mode)
            return
        parent = self.ensure_dir(parts[:-1])
        name = parts[-1]
        parent.children[name] = Node(name, False, mode, data)

    def stats(self):
        """Return (directories, files, bytes) of the whole file system."""
        dirs, files = count_nodes(self.root)
        return dirs, files, total_size(self.root)
