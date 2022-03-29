from unittest import TestCase

from aac.lang.context_manager import get_active_context
from aac.plugins.plugin_manager import get_validator_plugins
from aac.validate._validate_definition import validate_definition

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_field_entry,
)


class TestValidateDefinition(TestCase):
    def test__validate_definition_data_with_valid_field(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_data_definition("Empty Data", [test_field])
        test_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        actual_results = validate_definition(test_definition, validation_plugins, test_context)

        self.assertGreater(len(actual_results), 0)

        for result in actual_results:
            self.assertTrue(result.is_valid)

    def test__validate_definition_data_with_invalid_field(self):
        test_field = create_field_entry("TestField", "striiiiing")
        test_definition = create_data_definition("Empty Data", [test_field])
        test_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        actual_results = validate_definition(test_definition, validation_plugins, test_context)

        self.assertGreater(len(actual_results), 0)

        for result in actual_results:
            self.assertFalse(result.is_valid)
