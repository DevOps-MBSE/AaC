from unittest import TestCase

from aac.context.language_context import LanguageContext


class TestDefinition(TestCase):

    def test_get_root_key(self):
        context = LanguageContext()
        definition = context.get_definition_by_name("Schema")
        self.assertEqual(definition.get_root_key(), "schema")

        definition = context.get_definition_by_name("Field")
        self.assertEqual(definition.get_root_key(), "schema")

        definition = context.get_definition_by_name("string")
        self.assertEqual(definition.get_root_key(), "primitive")

        definition = context.get_definition_by_name("abstract")
        self.assertEqual(definition.get_root_key(), "modifier")
        
    def test_to_yaml(self):
        context = LanguageContext()
        definition = context.get_definition_by_name("Schema")
        yaml = definition.to_yaml()
        self.assertIn("schema:", yaml)
        self.assertIn("name: Schema", yaml)
