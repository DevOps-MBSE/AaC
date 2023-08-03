from aac.cli.builtin_commands.validate.validate_impl import validate
from aac.io.constants import DEFINITION_SEPARATOR, AAC_DOCUMENT_EXTENSION
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_failure, assert_plugin_success, assert_validation_failure
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_field_entry,
    create_model_definition,
    create_schema_definition,
)
from tests.helpers.io import TemporaryAaCTestFile


class TestValidateCommand(ActiveContextTestCase):
    def test_validate_command_succeeds_with_valid_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        with TemporaryAaCTestFile(valid_model.content) as valid_model_file:
            result = validate(valid_model_file.name)

            assert_plugin_success(result)
            self.assertIn(f"{valid_model_file.name} is valid", result.get_messages_as_string())

    def test_validate_command_fails_with_invalid_definition(self):
        invalid_model = create_model_definition("Invalid Model", "An invalid model.", [create_behavior_entry("a behavior with an invalid type", "invalid")])
        with TemporaryAaCTestFile(invalid_model.content) as invalid_model_file:
            result = validate(invalid_model_file.name)

            assert_validation_failure(result)
            self.assertIn("Failed to validate", result.get_messages_as_string())
            self.assertIn("Undefined type 'invalid'", result.get_messages_as_string())

    def test_validate_command_specify_definition_name_succeeds_with_valid_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        valid_schema = create_schema_definition("Test Schema", fields=[create_field_entry(DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING)])

        TEST_CONTENT = DEFINITION_SEPARATOR.join([valid_model.to_yaml(), valid_schema.to_yaml()])
        with TemporaryAaCTestFile(TEST_CONTENT) as valid_model_file:
            result = validate(valid_model_file.name, valid_model.name)

            assert_plugin_success(result)
            self.assertIn(f"{valid_model_file.name} is valid", result.get_messages_as_string())
            self.assertIn(valid_model.name, result.get_messages_as_string())

    def test_validate_command_specify_definition_name_fails_with_missing_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        valid_schema = create_schema_definition("Test Schema", fields=[create_field_entry(DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING)])

        TEST_CONTENT = DEFINITION_SEPARATOR.join([valid_model.to_yaml(), valid_schema.to_yaml()])
        with TemporaryAaCTestFile(TEST_CONTENT) as valid_model_file:
            undefined_definition_name = f"{valid_model.name}_v2"
            result = validate(valid_model_file.name, undefined_definition_name)

            assert_plugin_failure(result)
            error_message_as_lines = result.get_messages_as_string().splitlines()
            self.assertIn(undefined_definition_name, error_message_as_lines[0])
            self.assertIn("not found", error_message_as_lines[0])
            self.assertIn(valid_model.name, error_message_as_lines[1])
            self.assertIn(valid_schema.name, error_message_as_lines[1])

            # This check will only work if we allow validate to pollute the active context for validation.
            active_context = get_active_context()
            self.assertFalse(active_context.is_definition_type(valid_model.name))
            self.assertFalse(active_context.is_definition_type(valid_schema.name))
