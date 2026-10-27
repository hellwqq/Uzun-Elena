"""Tests of the in-memory VFS loaded from ZIP archives."""
import os
import tempfile
import unittest

from shellemu.errors import ShellError
from shellemu.vfs import Vfs

from .helpers import build_zip, make_shell, run

SAMPLE = [
    ("a.txt", b"abc", 0o644),
    ("dir/b.txt", b"hello", 0o600),
    ("dir/sub/c.bin", bytes([0, 255, 7]), 0o755),
    ("empty/", b"", 0o700),
]


class VfsLoadTest(unittest.TestCase):
    """Check building the tree from archive members."""

    def test_empty_archive(self):
        """An archive without members gives an empty root."""
        vfs = Vfs.from_bytes(build_zip([]))
        self.assertEqual(vfs.stats(), (0, 0, 0))

    def test_tree_structure_and_data(self):
        """Parent directories are created, data stays binary."""
        vfs = Vfs.from_bytes(build_zip(SAMPLE))
        node = vfs.root.children["dir"].children["sub"].children["c.bin"]
        self.assertEqual(node.data, bytes([0, 255, 7]))
        self.assertEqual(vfs.stats(), (3, 3, 11))

    def test_modes_are_read_from_archive(self):
        """Permission bits come from the external attributes."""
        vfs = Vfs.from_bytes(build_zip(SAMPLE))
        self.assertEqual(vfs.root.children["dir"].children["b.txt"].mode, 0o600)
        self.assertEqual(vfs.root.children["empty"].mode, 0o700)

    def test_default_modes(self):
        """Members without permission bits get the usual defaults."""
        vfs = Vfs.from_bytes(build_zip([("x/y.txt", b"1", None)]))
        self.assertEqual(vfs.root.children["x"].mode, 0o755)
        self.assertEqual(vfs.root.children["x"].children["y.txt"].mode, 0o644)

    def test_unsafe_path_is_rejected(self):
        """Archives with .. in names are refused."""
        with self.assertRaises(ShellError):
            Vfs.from_bytes(build_zip([("../evil.txt", b"x", 0o644)]))

    def test_bad_archive(self):
        """Random bytes are not accepted as an archive."""
        with self.assertRaises(ShellError):
            Vfs.from_bytes(b"not a zip")

    def test_from_zip_missing_file(self):
        """A missing archive file is reported."""
        with self.assertRaises(ShellError):
            Vfs.from_zip("/no/such/vfs.zip")

    def test_from_zip_reads_file(self):
        """The archive is read from disk into memory."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "v.zip")
            with open(path, "wb") as handle:
                handle.write(build_zip(SAMPLE))
            vfs = Vfs.from_zip(path)
        self.assertEqual(vfs.source, path)
        self.assertEqual(vfs.stats()[1], 3)


class VfsInfoTest(unittest.TestCase):
    """Check the vfs-info service command."""

    def test_vfs_info(self):
        """vfs-info prints the statistics as key=value lines."""
        shell = make_shell(SAMPLE)
        self.assertEqual(
            run(shell, "vfs-info"),
            "source=<not set>\ndirectories=3\nfiles=3\nbytes=11",
        )

    def test_vfs_info_without_vfs(self):
        """A shell without a loaded archive has an empty VFS."""
        self.assertIn("files=0", run(make_shell(), "vfs-info"))

    def test_vfs_info_rejects_arguments(self):
        """vfs-info takes no arguments."""
        self.assertIn("too many", run(make_shell(), "vfs-info x"))


if __name__ == "__main__":
    unittest.main()
