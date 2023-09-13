from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_NAME_ENUM, DEFINITION_NAME_SCHEMA, DEFINITION_NAME_VALIDATION, ROOT_KEY_SCHEMA, ROOT_KEY_VALIDATION
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.hierarchy import get_root_definition_by_key
from aac.lang.hierarchy import get_definition_ancestry

from tests.helpers.parsed_definitions import create_schema_definition, create_enum_definition


class TestLangHierarchy(TestCase):

    def test_get_definition_ancestry_schema_definition(self):
        test_context = get_active_context(reload_context=True)

        test_definition = create_schema_definition("TestDefinition")
        test_context.add_definition_to_context(test_definition)

        actual_result = get_definition_ancestry(test_definition, test_context)
        expected_result = [
            get_definition_by_name(DEFINITION_NAME_SCHEMA, test_context.definitions),
            get_definition_by_name(test_definition.name, test_context.definitions),
        ]

        self.assertListEqual(expected_result, actual_result)

    def test_get_definition_ancestry_enum_definition(self):
        test_context = get_active_context(reload_context=True)

        enum_definition = create_enum_definition("Enum1", ["val1"])
        test_context.add_definition_to_context(enum_definition)

        actual_result = get_definition_ancestry(enum_definition, test_context)
        expected_result = [
            get_definition_by_name(DEFINITION_NAME_SCHEMA, test_context.definitions),
            get_definition_by_name(DEFINITION_NAME_ENUM, test_context.definitions),
            get_definition_by_name(enum_definition.name, test_context.definitions),
        ]

        self.assertListEqual(expected_result, actual_result)

    def test_get_root_structure_by_key_schema_definition(self):
        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(DEFINITION_NAME_SCHEMA, active_context.definitions)
        actual_result = get_root_definition_by_key(ROOT_KEY_SCHEMA, active_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_root_structure_by_key_validation_definition(self):
        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(DEFINITION_NAME_VALIDATION, active_context.definitions)
        actual_result = get_root_definition_by_key(ROOT_KEY_VALIDATION, active_context)

        self.assertEqual(expected_result, actual_result)
