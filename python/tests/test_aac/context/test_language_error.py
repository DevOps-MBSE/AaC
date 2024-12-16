from unittest import TestCase

from aac.context.language_context import LanguageContext
from aac.context.language_error import LanguageError

class TestLanguageError(TestCase):
    def test_language_error(self):
        try:
            raise LanguageError("message", "location")
        except LanguageError as e:
            self.assertEqual(str(e), "Error: message. Location: location")

        try:
            raise LanguageError(message="message", location="location")
        except LanguageError as e:
            self.assertEqual(str(e), "Error: message. Location: location")
