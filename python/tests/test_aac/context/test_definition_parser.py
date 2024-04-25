from unittest import TestCase

from aac.context.language_context import LanguageContext
from aac.context.definition_parser import DefinitionParser
from aac.in_out.parser._parse_source import parse


class TestDefinitionParser(TestCase):
    def test_load_definitions(self):
        parser = DefinitionParser()
        context = LanguageContext()
        definitions = parse(VALID_AAC_YAML_CONTENT)
        loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)
        self.assertTrue(loaded_definitions)
        self.assertEqual(len(loaded_definitions), 1)



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
