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

    def test_is_import(self):
        context = LanguageContext()
        definition = context.parse_and_load(IMPORT_DEFINITION)[0]
        self.assertTrue(definition.is_import())
        definition = context.get_definitions_by_name("Schema")[0]
        self.assertFalse(definition.is_import())

    def test_get_python_module_name(self):
        context = LanguageContext()
        definition = context.get_definitions_by_name("Schema")[0]
        module_name = definition.get_python_module_name()
        self.assertEqual(module_name, "aac.lang")

    def test_get_python_class_name(self):
        context = LanguageContext()
        definition = context.parse_and_load(DEFINITION_VALID)[0]
        class_name = definition.get_python_class_name()
        self.assertEqual(class_name, "ModelName")

    def test_get_fully_qualified_name(self):
        context = LanguageContext()
        definition = context.get_definitions_by_name("Schema")[0]
        name = definition.get_fully_qualified_name()
        self.assertEqual(name, "aac.lang.Schema")

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
        with self.assertRaises(TypeError):
            definition = Definition(            # noqa: F841
                name=schema_definition.name,
                package=schema_definition.package,
                content=123,
                source=schema_definition.source,
                structure=schema_definition.structure,
            )

    def test_get_python_module_name_default(self):
        context = LanguageContext()
        definition = context.parse_and_load(DEFINITION_VALID)[0]
        module_name = definition.get_python_module_name()
        self.assertEqual(module_name, "default")


IMPORT_DEFINITION = """
import:
  files:
    - ./structures.yaml
    - ../alarm_clock/structures.yaml
"""

DEFINITION_VALID = """
model:
    name: Model Name
"""

DEFINITION_INVALID_ROOT_KEY = """
notaroot:
    name: notaroot
"""
