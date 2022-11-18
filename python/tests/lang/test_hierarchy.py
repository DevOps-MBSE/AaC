from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.hierarchy import get_root_definition_by_key
from aac.lang.hierarchy import get_definition_ancestry

from tests.helpers.parsed_definitions import create_schema_definition, create_enum_definition


class TestLangHierarchy(TestCase):

    def test_get_definition_ancestry_schema_definition(self):
        test_context = get_active_context(reload_context=True)

        schema_definition = create_schema_definition("TestDefinition")
        test_context.add_definition_to_context(schema_definition)

        actual_result = get_definition_ancestry(schema_definition, test_context)
        expected_result = [
            get_definition_by_name("schema", test_context.definitions),
            get_definition_by_name(schema_definition.name, test_context.definitions),
        ]

        self.assertListEqual(expected_result, actual_result)

    def test_get_definition_ancestry_enum_definition(self):
        test_context = get_active_context(reload_context=True)

        enum_definition = create_enum_definition("Enum1", ["val1"])
        test_context.add_definition_to_context(enum_definition)

        actual_result = get_definition_ancestry(enum_definition, test_context)
        expected_result = [
            get_definition_by_name("schema", test_context.definitions),
            get_definition_by_name("enum", test_context.definitions),
            get_definition_by_name(enum_definition.name, test_context.definitions),
        ]

        self.assertListEqual(expected_result, actual_result)

    def test_get_root_structure_by_key_schema_definition(self):
        target_definition_key = "schema"

        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(target_definition_key, active_context.definitions)
        actual_result = get_root_definition_by_key(target_definition_key, active_context.definitions)

        self.assertEqual(expected_result, actual_result)

    def test_get_root_structure_by_key_validation_definition(self):
        target_definition_key = "validation"
        target_definition_name = "Validation"

        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(target_definition_name, active_context.definitions)
        actual_result = get_root_definition_by_key(target_definition_key, active_context.definitions)

        self.assertEqual(expected_result, actual_result)
