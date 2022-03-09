"""
Unit tests for the aac.definition_helpers module.
"""

from unittest import TestCase

from aac import definition_helpers
from aac.spec import core


class TestDefinitionHelpers(TestCase):
    """
    Unit test class for aac.definition_helpers module.
    """

    def test_get_models_by_type(self):
        """
        Unit test for the definition_helpers.get_models_by_type method.
        """
        aac_data, aac_enums = core.get_aac_spec()
        num_data = len(aac_data)
        num_enums = len(aac_enums)
        num_models = 0
        all_aac = aac_data | aac_enums
        self.assertEqual(len(definition_helpers.get_models_by_type(all_aac, "data")), num_data)
        self.assertEqual(len(definition_helpers.get_models_by_type(all_aac, "enum")), num_enums)
        self.assertEqual(len(definition_helpers.get_models_by_type(all_aac, "model")), num_models)

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
