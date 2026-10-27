"""Emulator configuration taken from the command line."""
import argparse
from dataclasses import dataclass

UNSET = "<not set>"


@dataclass
class Config:
    """Parameters of one emulator run."""

    vfs_path: str = ""
    script_path: str = ""

    def items(self):
        """Return the parameters as (key, value) pairs in fixed order."""
        return [
            ("vfs_path", self.vfs_path or UNSET),
            ("script_path", self.script_path or UNSET),
        ]

    def dump(self):
        """Format the parameters as key=value lines."""
        return "\n".join(f"{key}={value}" for key, value in self.items())


def build_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="UNIX-like shell emulator with an in-memory VFS.",
    )
    parser.add_argument(
        "--vfs",
        default="",
        metavar="PATH",
        help="path to the physical location of the VFS",
    )
    parser.add_argument(
        "--script",
        default="",
        metavar="PATH",
        help="path to the startup script with emulator commands",
    )
    return parser


def parse_args(argv=None):
    """Parse command line arguments into a Config object."""
    namespace = build_parser().parse_args(argv)
    return Config(vfs_path=namespace.vfs, script_path=namespace.script)
