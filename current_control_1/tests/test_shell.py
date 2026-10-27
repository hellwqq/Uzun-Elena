"""Tests of the shell loop and the stage 1 commands."""
import unittest

from .helpers import make_shell, run


class ShellTest(unittest.TestCase):
    """Check prompt, placeholders and error handling."""

    def test_prompt_uses_real_data(self):
        """The prompt looks like user@host:~$ ."""
        shell = make_shell()
        self.assertEqual(shell.prompt(), f"{shell.user}@{shell.host}:~$ ")
        self.assertTrue(shell.user and shell.host)

    def test_ls_stub_prints_name_and_arguments(self):
        """The placeholder echoes the command and its arguments."""
        shell = make_shell()
        self.assertEqual(run(shell, 'ls -l "a b"'), "ls ['-l', 'a b']")

    def test_cd_stub_prints_name_and_arguments(self):
        """The cd placeholder behaves like the ls placeholder."""
        self.assertEqual(run(make_shell(), "cd /usr"), "cd ['/usr']")

    def test_unknown_command(self):
        """Unknown commands are reported."""
        self.assertEqual(run(make_shell(), "foo"), "foo: command not found")

    def test_syntax_error(self):
        """Parser errors are shown to the user, the shell goes on."""
        shell = make_shell()
        self.assertIn("syntax error", run(shell, 'ls "x'))
        self.assertTrue(shell.running)

    def test_blank_line(self):
        """A blank line prints nothing."""
        self.assertEqual(run(make_shell(), "   "), "")

    def test_exit(self):
        """exit stops the shell and accepts a code."""
        shell = make_shell()
        run(shell, "exit 3")
        self.assertFalse(shell.running)
        self.assertEqual(shell.exit_code, 3)

    def test_exit_errors(self):
        """exit validates its arguments."""
        shell = make_shell()
        self.assertIn("numeric", run(shell, "exit abc"))
        self.assertIn("too many", run(shell, "exit 1 2"))
        self.assertTrue(shell.running)


if __name__ == "__main__":
    unittest.main()
