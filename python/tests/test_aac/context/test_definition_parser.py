from unittest import TestCase

from aac.context.language_context import LanguageContext
from aac.context.definition_parser import DefinitionParser
from aac.in_out.parser import parse, ParserError


class TestDefinitionParser(TestCase):
    def test_load_definitions_pass(self):
        parser = DefinitionParser()
        context = LanguageContext()
        definitions = parse(VALID_AAC_YAML_CONTENT)
        loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)
        self.assertIsNotNone(definitions[0].instance)
        self.assertEqual(len(loaded_definitions), 1)
        self.assertEqual(definitions[0].name, "TestSchema")
        self.assertEqual(loaded_definitions, definitions)
        self.assertEqual(len(definitions[0].instance.fields), 4)

    def test_load_definitions_fail(self):
        parser = DefinitionParser()
        context = LanguageContext()
        with self.assertRaises(ParserError) as e:
            definitions = parse(INVALID_AAC_YAML_CONTENT)
            loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)



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

INVALID_AAC_YAML_CONTENT = """
schema:
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
