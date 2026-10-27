"""Command line parser with support for quoted arguments."""
from .errors import ShellError

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
ESCAPE = "\\"
COMMENT = "#"


class _Scanner:
    """State of the tokenizer while it scans one input line."""

    def __init__(self, line):
        """Prepare the scanner for the given line."""
        self.line = line
        self.pos = 0
        self.words = []
        self.chars = []
        self.has_word = False

    def peek(self):
        """Return the next character without consuming it."""
        if self.pos < len(self.line):
            return self.line[self.pos]
        return ""

    def next_char(self):
        """Consume and return the next character."""
        char = self.peek()
        self.pos += 1
        return char

    def add(self, text):
        """Append text to the word that is being collected."""
        self.chars.append(text)
        self.has_word = True

    def finish_word(self):
        """Store the collected word, keeping empty quoted words."""
        if self.has_word:
            self.words.append("".join(self.chars))
        self.chars = []
        self.has_word = False

    def read_single(self):
        """Read text up to the closing single quote."""
        end = self.line.find(SINGLE_QUOTE, self.pos)
        if end < 0:
            raise ShellError("syntax error: unterminated single quote")
        self.add(self.line[self.pos:end])
        self.pos = end + 1

    def read_double(self):
        """Read text up to the closing double quote."""
        self.has_word = True
        while self.pos < len(self.line):
            char = self.next_char()
            if char == DOUBLE_QUOTE:
                return
            if char == ESCAPE and self.peek() in (DOUBLE_QUOTE, ESCAPE):
                char = self.next_char()
            self.add(char)
        raise ShellError("syntax error: unterminated double quote")

    def read_escape(self):
        """Take the character after a backslash literally."""
        if self.pos >= len(self.line):
            raise ShellError("syntax error: trailing backslash")
        self.add(self.next_char())

    def run(self):
        """Scan the whole line and return the list of words."""
        while self.pos < len(self.line):
            char = self.next_char()
            if char.isspace():
                self.finish_word()
            elif char == COMMENT and not self.has_word:
                break
            elif char == SINGLE_QUOTE:
                self.read_single()
            elif char == DOUBLE_QUOTE:
                self.read_double()
            elif char == ESCAPE:
                self.read_escape()
            else:
                self.add(char)
        self.finish_word()
        return self.words


def parse_line(line):
    """Split an input line into words.

    Single and double quotes group words with spaces, a backslash
    escapes the next character, an unquoted word starting with '#'
    begins a comment. Raises ShellError for unbalanced quotes.
    """
    return _Scanner(line).run()
