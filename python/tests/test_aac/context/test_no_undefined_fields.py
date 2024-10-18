from unittest import TestCase
from aac.context.language_context import LanguageContext
from aac.context.language_error import LanguageError
from aac.in_out.parser._parser_error import ParserError


class TestNoUndefinedFields(TestCase):
    def test_no_extra_fields(self):
        context = LanguageContext()
        with self.assertRaises(LanguageError):
            definitions = context.parse_and_load(BAD_EXTRA_FIELDS)
            context.remove_definitions(definitions)

        with self.assertRaises(LanguageError):
            definitions = context.parse_and_load(BAD_EXTRA_SUB_FIELDS)
            context.remove_definitions(definitions)

    def test_no_undefined_fields(self):
        context = LanguageContext()
        with self.assertRaises(ParserError):
            definitions = context.parse_and_load(EMPTY_FIELDS)



# we've got plenty of good cases in the default language definition, so just test the bad case
BAD_EXTRA_FIELDS = """
schema:
    name: One
    package: test.no_undefined_fields
    root: one
    not_defined_in_field: fail
    fields:
        - name: name
          type: string
          is_required: true
        - name: extra
          type: string
"""

BAD_EXTRA_SUB_FIELDS = """
schema:
    name: One
    package: test.no_undefined_fields
    root: one
    fields:
        - name: name
          type: string
          is_required: true
          not_defined_in_field: fail
        - name: extra
          type: string
"""

EMPTY_FIELDS = """
schema:
    name:
    package:
"""
