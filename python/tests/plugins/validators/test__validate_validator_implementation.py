from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import ROOT_KEY_VALIDATION
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.plugin import Plugin
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution
from aac.plugins.validators.validator_implementation import (
    _get_plugin_definitions,
    _get_plugin_validations,
    validate_validator_implementations,
)

from tests.helpers.assertion import assert_definitions_equal
from tests.helpers.parsed_definitions import create_plugin_definition, create_validation_definition, create_validation_entry


class TestValidationImplementPlugin(TestCase):
    def test_validation_module_register_validators(self):
        actual_validator_plugins = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key(ROOT_KEY_VALIDATION, _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        validation_definition = validation_definitions[0]
        expected_definition_validation = DefinitionValidationContribution(
            name=validation_definition.name, definition=validation_definition, validation_function=(lambda x: x)
        )
        self.assertEqual(expected_definition_validation.name, actual_validator_plugins[0].name)
        assert_definitions_equal(expected_definition_validation.definition, actual_validator_plugins[0].definition)

    def test_validate_validator_implementations_validate_validation_success(self):
        test_active_context = get_active_context(reload_context=True)

        validation_definitions = test_active_context.get_definitions_by_root_key(ROOT_KEY_VALIDATION)
        self.assertGreater(len(validation_definitions), 0)

        test_validation_definition = validation_definitions[0]

        validation_definition = test_active_context.get_definition_by_name("Validation")

        actual_result = validate_validator_implementations(
            test_validation_definition, validation_definition, test_active_context
        )

        self.assertTrue(actual_result.is_valid())

    def test_validate_validator_implementations_validate_user_defined_validation_fails(self):
        test_active_context = get_active_context(reload_context=True)

        test_validation_name = "Test validation"
        test_validation_entry = create_validation_entry(test_validation_name)
        test_validation_definition = create_validation_definition(test_validation_name)
        test_validation_contribution = DefinitionValidationContribution(test_validation_name, test_validation_definition, None)

        test_plugin_name = "Test Plugin"
        test_plugin_definition = create_plugin_definition(test_plugin_name, definition_validations=[test_validation_entry])
        test_plugin = Plugin(test_plugin_name)
        test_plugin.register_definitions([test_plugin_definition, test_validation_definition])
        test_plugin.register_definition_validations([test_validation_contribution])

        validation_definition = test_active_context.get_definition_by_name("Validation")

        # Valid when the validator is contributed by an inactive plugin
        result = validate_validator_implementations(test_validation_definition, validation_definition, test_active_context)
        self.assertTrue(result.is_valid())

        # Invalid when the validator is contributed by an active plugin
        test_active_context.activate_plugin(test_plugin)
        result = validate_validator_implementations(test_validation_definition, validation_definition, test_active_context)
        self.assertFalse(result.is_valid())
        self.assertEqual(result.findings.get_error_findings()[0].location.location, SourceLocation(1, 8, 20, 15))
