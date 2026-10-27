"""Tests of the command line parser."""
import unittest

from shellemu.errors import ShellError
from shellemu.parser import parse_line


class ParserTest(unittest.TestCase):
    """Check splitting of input lines into words."""

    def test_plain_words(self):
        """Words are split on any amount of whitespace."""
        self.assertEqual(parse_line("ls   -l \t /tmp"), ["ls", "-l", "/tmp"])

    def test_empty_line(self):
        """An empty or blank line gives no words."""
        self.assertEqual(parse_line("   "), [])

    def test_double_quotes(self):
        """Double quotes keep spaces inside one argument."""
        self.assertEqual(parse_line('ls "my docs" x'), ["ls", "my docs", "x"])

    def test_single_quotes(self):
        """Single quotes take everything literally."""
        self.assertEqual(parse_line("cd 'a \"b\" c'"), ["cd", 'a "b" c'])

    def test_empty_quoted_argument(self):
        """An empty pair of quotes is an empty argument."""
        self.assertEqual(parse_line('ls "" x'), ["ls", "", "x"])

    def test_adjacent_quotes_are_joined(self):
        """Quoted and unquoted pieces without spaces form one word."""
        self.assertEqual(parse_line('a"b c"d'), ["ab cd"])

    def test_escapes(self):
        """A backslash escapes a space and a quote."""
        self.assertEqual(parse_line(r'a\ b "c\"d"'), ["a b", 'c"d'])

    def test_comment(self):
        """Text after an unquoted # is ignored."""
        self.assertEqual(parse_line("ls x # note"), ["ls", "x"])
        self.assertEqual(parse_line('echo "#x"'), ["echo", "#x"])

    def test_unterminated_quotes(self):
        """Unbalanced quotes are reported as errors."""
        for line in ('ls "abc', "ls 'abc", "ls abc\\"):
            with self.assertRaises(ShellError):
                parse_line(line)


if __name__ == "__main__":
    unittest.main()
