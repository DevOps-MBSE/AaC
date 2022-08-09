from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.plugins.validators import ValidatorPlugin
from aac.plugins.validators.validator_implementation import _get_plugin_definitions, _get_plugin_validations, validate_validator_implementations

from tests.helpers.parsed_definitions import create_validation_definition


class TestValidationImplementPlugin(TestCase):

    def test_validation_module_register_validators(self):
        actual_validator_plugins = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key("validation", _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        validation_definition = validation_definitions[0]
        expected_validator_plugin = ValidatorPlugin(
            name=validation_definition.name, definition=validation_definition, validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugins[0].name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugins[0].definition)

    def test_validate_validator_implementations_validate_validation_success(self):
        test_active_context = get_active_context(reload_context=True)

        validation_definitions = list(filter(lambda definition: definition.get_root_key() == "validation", test_active_context.definitions))
        self.assertGreater(len(validation_definitions), 0)

        test_validation_definition = validation_definitions[0]

        validation_definition = test_active_context.get_definition_by_name("Validation")

        actual_result = validate_validator_implementations(test_validation_definition, validation_definition, test_active_context)

        self.assertTrue(actual_result.is_valid)

    def test_validate_validator_implementations_validate_user_defined_validation_fails(self):
        test_active_context = get_active_context(reload_context=True)

        validation_name = "TestValidationThatNoOneWillEverReplicate"
        test_validation_definition = create_validation_definition(validation_name)

        validation_definition = test_active_context.get_definition_by_name("Validation")

        actual_result = validate_validator_implementations(test_validation_definition, validation_definition, test_active_context)

        self.assertFalse(actual_result.is_valid)
