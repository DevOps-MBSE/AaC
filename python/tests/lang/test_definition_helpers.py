"""
Unit tests for the aac.definition_helpers module.
"""

from unittest import TestCase

from aac.lang import definition_helpers
from aac.parser.ParsedDefinition import ParsedDefinition
from aac.spec import core


class TestDefinitionHelpers(TestCase):
    """
    Unit test class for aac.definition_helpers module.
    """

    def test_get_models_by_type(self):
        """
        Unit test for the definition_helpers.get_models_by_type method.
        """
        def filter_by_root(definition: ParsedDefinition, root_key: str):
            return (definition.get_root_key() == root_key)

        aac_core_definitions = core.get_aac_spec()
        data_definitions = list(filter(lambda definition: filter_by_root(definition, "data"), aac_core_definitions))
        enum_definitions = list(filter(lambda definition: filter_by_root(definition, "enum"), aac_core_definitions))
        model_definitions = list(filter(lambda definition: filter_by_root(definition, "model"), aac_core_definitions))

        self.assertEqual(len(definition_helpers.get_definitions_by_type(aac_core_definitions, "data")), len(data_definitions))
        self.assertEqual(len(definition_helpers.get_definitions_by_type(aac_core_definitions, "enum")), len(enum_definitions))
        self.assertEqual(len(definition_helpers.get_definitions_by_type(aac_core_definitions, "model")), len(model_definitions))

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
        data_model_types = definition_helpers.search(data_entry, ["data", "fields", "type"])

        self.assertCountEqual(data_model_types, expected)
