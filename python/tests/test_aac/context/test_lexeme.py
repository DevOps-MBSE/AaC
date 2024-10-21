from unittest import TestCase
from aac.context.lexeme import Lexeme
from aac.context.source_location import SourceLocation


class TestLexeme(TestCase):
    def test_lexeme(self):
        loc = SourceLocation(1, 2, 3, 4)
        src = "my_source.aac"
        value = "my_value"

        lex_one = Lexeme(loc, src, value)
        lex_two = Lexeme(loc, src, value)

        self.assertEqual(lex_one, lex_two)

        string_value = str(lex_one)
        self.assertIsInstance(string_value, str)
        self.assertGreater(len(string_value), 0)

    def test_lexeme_fail(self):
        loc = SourceLocation(1, 2, 3, 4)
        src = "my_source.aac"
        value = "my_value"

        lex_one = Lexeme(loc, src, value)
        lex_two = Lexeme(loc, value, src)

        self.assertNotEqual(lex_one, lex_two)
