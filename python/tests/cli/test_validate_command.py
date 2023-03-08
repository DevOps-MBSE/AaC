from aac.cli.builtin_commands.validate.validate_impl import validate
from aac.io.constants import DEFINITION_SEPARATOR
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_failure, assert_plugin_success, assert_validation_failure
from tests.helpers.parsed_definitions import create_field_entry, create_model_definition, create_schema_definition
from tests.helpers.io import temporary_test_file


class TestValidateCommand(ActiveContextTestCase):
    def test_validate_command_succeeds_with_valid_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        with temporary_test_file(valid_model.content) as valid_model_file:
            result = validate(valid_model_file.name)

            assert_plugin_success(result)
            self.assertIn(f"{valid_model_file.name} is valid", result.get_messages_as_string())

    def test_validate_command_fails_with_invalid_definition(self):
        invalid_schema = create_schema_definition("Invalid Schema", "An invalid schema.", fields=[create_field_entry("invalid_type", "invalid")])
        with temporary_test_file(invalid_schema.content) as invalid_model_file:
            result = validate(invalid_model_file.name)

            assert_validation_failure(result)
            self.assertIn("Failed to validate", result.get_messages_as_string())
            self.assertIn("Undefined type 'invalid'", result.get_messages_as_string())

    def test_validate_command_specify_definition_name_succeeds_with_valid_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        valid_schema = create_schema_definition("Test Schema", fields=[create_field_entry(DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING)])

        TEST_CONTENT = DEFINITION_SEPARATOR.join([valid_model.to_yaml(), valid_schema.to_yaml()])
        with temporary_test_file(TEST_CONTENT) as valid_model_file:
            result = validate(valid_model_file.name, valid_model.name)

            assert_plugin_success(result)
            self.assertIn(f"{valid_model_file.name} is valid", result.get_messages_as_string())
            self.assertIn(valid_model.name, result.get_messages_as_string())

    def test_validate_command_specify_definition_name_fails_with_missing_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        valid_schema = create_schema_definition("Test Schema", fields=[create_field_entry(DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING)])

        TEST_CONTENT = DEFINITION_SEPARATOR.join([valid_model.to_yaml(), valid_schema.to_yaml()])
        with temporary_test_file(TEST_CONTENT) as valid_model_file:
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
