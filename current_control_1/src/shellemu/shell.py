"""Interactive shell loop."""
import getpass
import socket
import sys

from .commands import COMMANDS
from .config import Config
from .errors import ShellError
from .parser import parse_line
from .vfs import Vfs


def _current_user():
    """Return the name of the OS user running the emulator."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return "user"


class Shell:
    """State of the emulator and the read-eval-print loop."""

    def __init__(self, config=None, out=None):
        """Create a shell with the given parameters and output stream."""
        self.config = Config() if config is None else config
        self.out = sys.stdout if out is None else out
        self.vfs = Vfs()
        self.running = True
        self.exit_code = 0
        self.user = _current_user()
        self.host = socket.gethostname()

    def prompt(self):
        """Build the input prompt from real data of the host OS."""
        return f"{self.user}@{self.host}:~$ "

    def write(self, text):
        """Print one line of text to the output stream."""
        print(text, file=self.out)

    def dispatch(self, words):
        """Find the command named by the first word and run it."""
        if not words:
            return ""
        handler = COMMANDS.get(words[0])
        if handler is None:
            raise ShellError(f"{words[0]}: command not found")
        return handler(self, words[1:])

    def execute(self, line):
        """Run one input line; return False if it ended with an error."""
        try:
            output = self.dispatch(parse_line(line))
        except ShellError as err:
            self.write(str(err))
            return False
        if output:
            self.write(output)
        return True

    def run_repl(self):
        """Read commands from the user until exit or end of input."""
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                self.write("")
                break
            except KeyboardInterrupt:
                self.write("^C")
                continue
            self.execute(line)

    def run_script(self, path):
        """Execute a script file, showing input and output like a dialog.

        Lines that fail are reported and skipped, execution goes on.
        """
        try:
            with open(path, encoding="utf-8-sig") as handle:
                lines = handle.read().splitlines()
        except OSError as err:
            raise ShellError(
                f"script: cannot read '{path}': {err.strerror}"
            ) from err
        for line in lines:
            if not self.running:
                break
            if line.strip():
                self.write(self.prompt() + line)
                self.execute(line)
