from unittest import TestCase

from aac.context.language_context import LanguageContext
from aac.context.language_error import LanguageError
from aac.context.definition_parser import DefinitionParser
from aac.in_out.parser import parse, ParserError


class TestDefinitionParser(TestCase):
    def test_find_definitions_by_name(self):
        context = LanguageContext()
        definitions = context.get_definitions_by_name("Schema")
        self.assertEqual(len(definitions), 1)
        self.assertEqual(definitions[0].name, "Schema")
        self.assertIsNotNone(definitions[0].instance)

        context.parse_and_load(VALID_AAC_YAML_CONTENT_SPACE_IN_NAME)
        definitions = context.get_definitions_by_name("Test Schema2")
        self.assertEqual(definitions[0].name, "Test Schema2")

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
        with self.assertRaises(ParserError):
            definitions = parse(INVALID_AAC_YAML_CONTENT)
            loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)  # noqa: F841
            self.assertFalse(definitions[0].source.is_loaded_in_context)

    def test_load_incomplete_definition(self):
        parser = DefinitionParser()
        context = LanguageContext()
        with self.assertRaises(ParserError):
            definitions = parse(SCHEMA_WITH_INCOMPLETE_FIELD)
            loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)  # noqa: F841
            self.assertFalse(definitions[0].source.is_loaded_in_context)

    def test_load_bad_enum(self):
        parser = DefinitionParser()
        context = LanguageContext()
        with self.assertRaises(ParserError):
            definitions = parse(SCHEMA_WITH_BAD_ENUM)
            loaded_definitions = parser.load_definitions(context=context, parsed_definitions=definitions)  # noqa: F841
            self.assertFalse(definitions[0].source.is_loaded_in_context)

    def test_load_empty_name(self):
        parser = DefinitionParser()
        context = LanguageContext()
        definition = parse(VALID_AAC_YAML_CONTENT)
        definition[0].name = "1schema_test"
        try:
            loaded_definition = parser.load_definitions(context=context, parsed_definitions=definition)
        except LanguageError as e:
            self.assertNotEqual(e.location, "Unknown location")

    def test_empty_field_value_not_list(self):
        context = LanguageContext()
        try:
            loaded_definition = context.parse_and_load(SCHEMA_WITH_EMPTY_FIELD_VALUE_NOT_LIST)
        except ParserError as e:
            self.assertIn("Missing value for field: type.", e.errors)


    def test_empty_field_value_list(self):
        context = LanguageContext()
        try:
            loaded_definition = context.parse_and_load(SCHEMA_WITH_EMPTY_FIELD_VALUE_LIST)
        except ParserError as e:
            self.assertIn("Missing value for field: fields.", e.errors)


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

VALID_AAC_YAML_CONTENT_SPACE_IN_NAME = """
schema:
  name: Test Schema2
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

SCHEMA_WITH_INCOMPLETE_FIELD = """
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
    - name: not_used
""".strip()

SCHEMA_WITH_BAD_ENUM= """
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
   enum:
    name: bad_enum
    values:
        - bad_value
        - bad_value
""".strip()

SCHEMA_WITH_EMPTY_FIELD_VALUE_NOT_LIST= """
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
      type:
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

SCHEMA_WITH_EMPTY_FIELD_VALUE_LIST= """
schema:
  name: TestSchema
  description: |
    This is a test schema.
  fields:
""".strip()
