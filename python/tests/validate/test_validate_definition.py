from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.validate._validate import _validate_definition

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_field_entry,
)


class TestValidateDefinition(ActiveContextTestCase):
    def test__validate_definition_schema_with_valid_field(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_schema_definition("Test", fields=[test_field])
        test_context = get_active_context(reload_context=True)

        validation_plugins = test_context.get_validator_plugins()

        actual_results = _validate_definition(test_definition, validation_plugins, test_context)

        self.assertGreater(len(actual_results), 0)

        for result in actual_results:
            self.assertTrue(result.is_valid)

    def test__validate_definition_schema_with_invalid_field(self):
        test_field = create_field_entry("TestField", "striiiiing")
        test_definition = create_schema_definition("Test", fields=[test_field])
        test_context = get_active_context(reload_context=True)

        validation_plugins = test_context.get_validator_plugins()

        actual_results = _validate_definition(test_definition, validation_plugins, test_context)

        self.assertGreater(len(actual_results), 0)

        invalid_results = list(filter(lambda result: not result.is_valid(), actual_results))
        self.assertEqual(len(invalid_results), 1)
        self.assertIn("undefined", invalid_results[0].get_messages_as_string().lower())
