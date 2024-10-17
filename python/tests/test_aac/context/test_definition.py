from unittest import TestCase

from aac.context.definition import Definition
from aac.context.language_context import LanguageContext


class TestDefinition(TestCase):

    def test_get_root_key(self):
        context = LanguageContext()
        definition = context.get_definitions_by_name("Schema")
        self.assertEqual(definition[0].get_root_key(), "schema")

        definition = context.get_definitions_by_name("Field")
        self.assertEqual(definition[0].get_root_key(), "schema")

        definition = context.get_definitions_by_name("string")
        self.assertEqual(definition[0].get_root_key(), "primitive")

        definition = context.get_definitions_by_name("abstract")
        self.assertEqual(definition[0].get_root_key(), "modifier")

    def test_to_yaml(self):
        context = LanguageContext()
        definition = context.get_definitions_by_name("Schema")
        yaml = definition[0].to_yaml()
        self.assertIn("schema:", yaml)
        self.assertIn("name: Schema", yaml)

    def test_definition_fail_incorrect_types(self):
        context = LanguageContext()
        schema_definition = context.get_definitions_by_name("Schema")[0]
        with self.assertRaises(TypeError):
            # This is probably the worst way to make a definition, it should normally be handled by Language Context
            definition = Definition(
                name=123,
                package=schema_definition.package,
                content=schema_definition.content,
                source=schema_definition.source,
                structure=schema_definition.structure,
            )
        with self.assertRaises(TypeError):
            definition = Definition(            # noqa: F841
                name=schema_definition.name,
                package=123,
                content=schema_definition.content,
                source=schema_definition.source,
                structure=schema_definition.structure,
            )


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
