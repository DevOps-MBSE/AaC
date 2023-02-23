"""
Unit tests for the aac.definition_helpers module.
"""

from unittest import TestCase

from aac.lang.definitions.collections import (
    get_definitions_by_root_key,
)
from aac.lang.definitions.search import search
from aac.lang.definitions.definition import Definition
from aac.lang.spec import get_aac_spec


class TestDefinitionHelpers(TestCase):
    """
    Unit test class for aac.definition_helpers module.
    """

    def test_get_models_by_type(self):
        """
        Unit test for the definition_helpers.get_models_by_type method.
        """

        def filter_by_root(definition: Definition, root_key: str):
            return definition.get_root_key() == root_key

        aac_core_definitions = get_aac_spec()
        schema_definitions = list(filter(lambda definition: filter_by_root(definition, "schema"), aac_core_definitions))
        enum_definitions = list(filter(lambda definition: filter_by_root(definition, "enum"), aac_core_definitions))
        model_definitions = list(filter(lambda definition: filter_by_root(definition, "model"), aac_core_definitions))

        self.assertEqual(len(get_definitions_by_root_key("schema", aac_core_definitions)), len(schema_definitions))
        self.assertEqual(len(get_definitions_by_root_key("enum", aac_core_definitions)), len(enum_definitions))
        self.assertEqual(len(get_definitions_by_root_key("model", aac_core_definitions)), len(model_definitions))

    def test_search(self):
        """
        Unit test for the definition_helpers.search method.
        """
        schema_entry = {
            "schema": {
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
        schema_field_types = search(schema_entry, ["schema", "fields", "type"])

        self.assertCountEqual(schema_field_types, expected)
