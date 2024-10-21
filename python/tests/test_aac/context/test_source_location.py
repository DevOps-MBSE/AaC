from unittest import TestCase
from aac.context.source_location import SourceLocation
from aac.context.language_context import LanguageContext


class TestSourceLocation(TestCase):
    def test_source_location(self):
        loc = SourceLocation(1, 2, 3, 4)
        self.assertIsInstance(loc.to_tuple(), tuple)

        loc2 = SourceLocation(2, 1, 3, 4)
        self.assertIsInstance(loc2.to_tuple(), tuple)

        loc3 = SourceLocation(1, 2, 4, 3)
        self.assertIsInstance(loc3.to_tuple(), tuple)
        self.assertNotEqual(loc, loc2, loc3)

    def test_source_location_mapping(self):
        context = LanguageContext()
        definition = context.parse_and_load(VALID_AAC_YAML_CONTENT)[0]
        lexemes = definition.lexemes

        self.assertEqual(lexemes[0].value, "schema")
        self.assertEqual(lexemes[0].location.to_tuple(), (0, 0, 0, 6))

        self.assertEqual(lexemes[1].value, "name")
        self.assertEqual(lexemes[1].location.to_tuple(), (1, 2, 10, 4))


    def test_source_location_incorrect_type(self):
        with self.assertRaises(TypeError):
            loc = SourceLocation("1", "2", "3", "4")  # noqa: F841

VALID_AAC_YAML_CONTENT = """
schema:
  name: TestSchema
  description: |
    This is a test schema.
  fields:
    - name: string_field
      type: string
      description: |
        This is a test field.
    - name: integer_field
      type: integer
      description: |
        This is a test field.
    - name: boolean_field
      type: boolean
      description: |
        This is a test field.
    - name: number_field
      type: number
      description: |
        This is a test field.
""".strip()
