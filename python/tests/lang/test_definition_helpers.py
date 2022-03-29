"""
Unit tests for the aac.definition_helpers module.
"""

from unittest import TestCase
from aac.lang.context_manager import get_active_context

from aac.lang.definition_helpers import (
    get_definition_by_name,
    get_definitions_by_root_key,
    get_definition_fields_and_types,
    search,
    search_definition,
)
from aac.parser import ParsedDefinition
from aac.spec import core
from tests.helpers.parsed_definitions import create_model_definition


class TestDefinitionHelpers(TestCase):
    """
    Unit test class for aac.definition_helpers module.
    """

    def test_get_models_by_type(self):
        """
        Unit test for the definition_helpers.get_models_by_type method.
        """

        def filter_by_root(definition: ParsedDefinition, root_key: str):
            return definition.get_root_key() == root_key

        aac_core_definitions = core.get_aac_spec()
        data_definitions = list(filter(lambda definition: filter_by_root(definition, "data"), aac_core_definitions))
        enum_definitions = list(filter(lambda definition: filter_by_root(definition, "enum"), aac_core_definitions))
        model_definitions = list(filter(lambda definition: filter_by_root(definition, "model"), aac_core_definitions))

        self.assertEqual(len(get_definitions_by_root_key("data", aac_core_definitions)), len(data_definitions))
        self.assertEqual(len(get_definitions_by_root_key("enum", aac_core_definitions)), len(enum_definitions))
        self.assertEqual(len(get_definitions_by_root_key("model", aac_core_definitions)), len(model_definitions))

    def test_search(self):
        """
        Unit test for the definition_helpers.search method.
        """
        data_entry = {
            "data": {
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "type", "type": "BehaviorType"},
                    {"name": "description", "type": "string"},
                    {"name": "tags", "type": "string[]"},
                    {"name": "input", "type": "Field[]"},
                    {"name": "output", "type": "Field[]"},
                    {"name": "acceptance", "type": "Scenario[]"},
                ],
                "name": "Behavior",
                "required": ["name", "type", "acceptance"],
            }
        }

        expected = [
            "string",
            "BehaviorType",
            "string",
            "string[]",
            "Field[]",
            "Field[]",
            "Scenario[]",
        ]
        data_model_types = search(data_entry, ["data", "fields", "type"])

        self.assertCountEqual(data_model_types, expected)

    def test_get_definition_field_types_model_type(self):
        text_context = get_active_context(reload_context=True)
        test_model = create_model_definition("TestModel")

        model_definition = get_definition_by_name("model", text_context.context_definitions)
        expected_fields = search_definition(model_definition, ["data", "fields"])
        self.assertGreater(len(expected_fields), 1)

        actual_result = get_definition_fields_and_types(test_model, text_context.context_definitions)

        self.assertEqual(len(expected_fields), len(actual_result))

        for expected_field in expected_fields:
            field_name = expected_field.get("name")
            field_type = expected_field.get("type")
            self.assertIn(field_name, actual_result)
            self.assertTrue(text_context.is_definition_type(field_type) or text_context.is_primitive_type(field_type))
