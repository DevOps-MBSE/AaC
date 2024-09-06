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
        context_definitions = parser.context.get_definitions_by_name(loaded_definitions[0].name)
        name = context_definitions[0].name

        self.assertEqual(name, loaded_definitions[0].name)
        self.assertIsNotNone(context_definitions[0].instance)
        self.assertEqual(len(context_definitions), 1)
        self.assertEqual(loaded_definitions, context_definitions)
        self.assertEqual(len(context_definitions[0].instance.fields), len(loaded_definitions[0].instance.fields))
        self.assertTrue(loaded_definitions[0].source.is_loaded_in_context)

    def test_load_definitions_fail(self):
        parser = DefinitionParser()
        context = LanguageContext()
        with self.assertRaises(ParserError) as e:
            definitions = parse(INVALID_AAC_YAML_CONTENT)
            loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)
            self.assertFalse(definitions[0].source.is_loaded_in_context)

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
