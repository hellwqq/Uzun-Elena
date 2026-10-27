"""Create sample ZIP archives used as VFS sources in the demo scripts.

Usage: python3 tools/make_vfs.py [OUTPUT_DIR]
"""
import os
import stat
import sys
import zipfile

DEFAULT_OUTPUT = os.path.join("examples", "vfs")
MODE_SHIFT = 16
BINARY_SAMPLE = bytes(range(0, 256, 5))


def add_dir(archive, name, mode=0o755):
    """Write an explicit directory entry into the archive."""
    info = zipfile.ZipInfo(name.rstrip("/") + "/")
    info.external_attr = (stat.S_IFDIR | mode) << MODE_SHIFT
    archive.writestr(info, b"")


def add_file(archive, name, data, mode=0o644):
    """Write a file with the given permission bits into the archive."""
    info = zipfile.ZipInfo(name)
    info.external_attr = (stat.S_IFREG | mode) << MODE_SHIFT
    archive.writestr(info, data)


def make_empty(path):
    """Create an archive without any members."""
    with zipfile.ZipFile(path, "w"):
        pass


def make_minimal(path):
    """Create an archive with a single file."""
    with zipfile.ZipFile(path, "w") as archive:
        add_file(archive, "hello.txt", b"Hello, VFS!\n")


def make_files(path):
    """Create an archive with several files in one directory."""
    with zipfile.ZipFile(path, "w") as archive:
        add_file(archive, "notes.txt", b"first note\nsecond note\n")
        add_file(archive, "todo.txt", b"1. write tests\n", 0o600)
        add_file(archive, "photo.bin", BINARY_SAMPLE)
        add_file(archive, "run.sh", b"#!/bin/sh\necho hi\n", 0o755)
        add_file(archive, "my docs/read me.txt", b"names with spaces\n")


def make_deep(path):
    """Create an archive with four levels of files and folders."""
    with zipfile.ZipFile(path, "w") as archive:
        add_file(archive, "README.txt", b"deep sample\n")
        add_dir(archive, "docs")
        add_file(archive, "docs/guide.txt", b"guide\n")
        add_file(archive, "docs/manual/intro.txt", b"intro\n")
        add_file(archive, "docs/manual/chapters/ch1.txt", b"one\n", 0o600)
        add_file(archive, "docs/manual/chapters/ch2.txt", b"two\n")
        add_file(archive, "src/main.py", b"print('hi')\n", 0o755)
        add_file(archive, "src/lib/util.py", b"VALUE = 1\n")
        add_file(archive, "src/lib/pkg/__init__.py", b"")
        add_file(archive, "bin/data.bin", BINARY_SAMPLE)
        add_dir(archive, "empty", 0o700)


SAMPLES = {
    "empty.zip": make_empty,
    "minimal.zip": make_minimal,
    "files.zip": make_files,
    "deep.zip": make_deep,
}


def main(argv):
    """Create all sample archives in the requested directory."""
    folder = argv[0] if argv else DEFAULT_OUTPUT
    os.makedirs(folder, exist_ok=True)
    for name, builder in SAMPLES.items():
        builder(os.path.join(folder, name))
        print(f"created {os.path.join(folder, name)}")


if __name__ == "__main__":
    main(sys.argv[1:])
