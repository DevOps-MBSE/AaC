from unittest import TestCase

from aac.lang import get_active_context
from aac.lang.definition_helpers import get_definition_by_name
from aac.lang.hierarchy import get_root_definition_by_key
from aac.lang.hierarchy import get_definition_ancestry

from tests.helpers.parsed_definitions import create_data_definition, create_enum_definition


class TestLangHierarchy(TestCase):

    def test_get_definition_ancestry_data_definition(self):
        test_context = get_active_context(reload_context=True)

        data_definition = create_data_definition("Data1")
        test_context.add_definition_to_context(data_definition)

        actual_result = get_definition_ancestry(data_definition, test_context)
        expected_result = [
            get_definition_by_name(test_context.context_definitions, "data"),
            get_definition_by_name(test_context.context_definitions, data_definition.name),
        ]

        self.assertListEqual(expected_result, actual_result)

    def test_get_definition_ancestry_enum_definition(self):
        test_context = get_active_context(reload_context=True)

        enum_definition = create_enum_definition("Enum1", ["val1"])
        test_context.add_definition_to_context(enum_definition)

        actual_result = get_definition_ancestry(enum_definition, test_context)
        expected_result = [
            get_definition_by_name(test_context.context_definitions, "data"),
            get_definition_by_name(test_context.context_definitions, "enum"),
            get_definition_by_name(test_context.context_definitions, enum_definition.name),
        ]

        self.assertListEqual(expected_result, actual_result)

    def test_get_root_structure_by_key_data_definition(self):
        target_definition_key = "data"

        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(active_context.context_definitions, target_definition_key)
        actual_result = get_root_definition_by_key(target_definition_key, active_context.context_definitions)

        self.assertEqual(expected_result, actual_result)

    def test_get_root_structure_by_key_validation_definition(self):
        target_definition_key = "validation"
        target_definition_name = "Validation"

        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(active_context.context_definitions, target_definition_name)
        actual_result = get_root_definition_by_key(target_definition_key, active_context.context_definitions)

        self.assertEqual(expected_result, actual_result)
