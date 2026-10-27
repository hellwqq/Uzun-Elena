"""Tests of command line parameters and the conf-dump command."""
import os
import tempfile
import unittest

from shellemu.config import UNSET, Config, parse_args
from shellemu.errors import ShellError

from .helpers import make_shell, run


class ConfigTest(unittest.TestCase):
    """Check parsing of arguments and key=value output."""

    def test_defaults(self):
        """Without arguments both parameters are empty."""
        config = parse_args([])
        self.assertEqual(config, Config("", ""))

    def test_values(self):
        """Both options are stored in the configuration."""
        config = parse_args(["--vfs", "a.zip", "--script", "s.emu"])
        self.assertEqual(config.vfs_path, "a.zip")
        self.assertEqual(config.script_path, "s.emu")

    def test_unknown_option_exits(self):
        """argparse stops the program on unknown options."""
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])

    def test_dump_format(self):
        """Parameters are printed as key=value lines."""
        text = Config("v.zip", "").dump()
        self.assertEqual(
            text.splitlines(),
            ["vfs_path=v.zip", f"script_path={UNSET}"],
        )

    def test_conf_dump_command(self):
        """conf-dump prints the parameters of the running shell."""
        shell = make_shell()
        shell.config = Config("x.zip", "y.emu")
        output = run(shell, "conf-dump")
        self.assertEqual(output, "vfs_path=x.zip\nscript_path=y.emu")

    def test_conf_dump_rejects_arguments(self):
        """conf-dump takes no arguments."""
        self.assertIn("too many", run(make_shell(), "conf-dump x"))


class ScriptTest(unittest.TestCase):
    """Check the execution of startup scripts."""

    def run_script(self, text):
        """Run a script with the given text and return the output."""
        shell = make_shell()
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "start.emu")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            shell.run_script(path)
        return shell, shell.out.getvalue()

    def test_input_and_output_are_shown(self):
        """The script lines are echoed after the prompt."""
        shell, output = self.run_script("cd x\n")
        self.assertIn(shell.prompt() + "cd x", output)
        self.assertIn("cd ['x']", output)

    def test_errors_are_skipped(self):
        """A failing line does not stop the script."""
        _, output = self.run_script("bad\nls\n")
        self.assertIn("bad: command not found", output)
        self.assertIn("ls []", output)

    def test_exit_stops_script(self):
        """Lines after exit are not executed."""
        shell, output = self.run_script("exit\nls\n")
        self.assertFalse(shell.running)
        self.assertNotIn("ls []", output)

    def test_missing_script(self):
        """A missing file is reported with ShellError."""
        with self.assertRaises(ShellError):
            make_shell().run_script("/no/such/script.emu")


if __name__ == "__main__":
    unittest.main()
