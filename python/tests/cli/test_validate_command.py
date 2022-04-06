from unittest import TestCase

from aac.cli.builtin_commands.validate.validate_impl import validate

from tests.helpers.assertion import assert_plugin_success, assert_validation_failure
from tests.helpers.parsed_definitions import create_behavior_entry, create_model_definition
from tests.helpers.io import temporary_test_file


class TestValidateCommand(TestCase):
    def test_validate_command_succeeds_with_valid_definition(self):
        valid_model = create_model_definition("Valid Model", "A valid model.")
        with temporary_test_file(valid_model.content) as valid_model_file:
            result = validate(valid_model_file.name)
            assert_plugin_success(result)

    def test_validate_command_fails_with_invalid_definition(self):
        invalid_model = create_model_definition("Invalid Model", "An invalid model.", [create_behavior_entry("not a component")])
        with temporary_test_file(invalid_model.content) as invalid_model_file:
            result = validate(invalid_model_file.name)
            assert_validation_failure(result)
