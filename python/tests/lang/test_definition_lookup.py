"""
Unit tests for the aac.definition_helpers module.
"""

from unittest import TestCase

from aac.lang import get_active_context
from aac.lang.definition_helpers import get_definition_by_name
from aac.lang.definition_lookup import get_root_definition_from_key


class TestDefinitionLookup(TestCase):

    def test_get_root_structure_from_key_data_definition(self):
        target_definition_key = "data"

        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(active_context.context_definitions, target_definition_key)
        actual_result = get_root_definition_from_key(target_definition_key, active_context.context_definitions)

        self.assertEqual(expected_result, actual_result)

    def test_get_root_structure_from_key_validation_definition(self):
        target_definition_key = "validation"
        target_definition_name = "Validation"

        active_context = get_active_context(reload_context=True)

        expected_result = get_definition_by_name(active_context.context_definitions, target_definition_name)
        actual_result = get_root_definition_from_key(target_definition_key, active_context.context_definitions)

        self.assertEqual(expected_result, actual_result)
