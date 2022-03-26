from unittest import TestCase

from aac.lang import get_active_context
from aac.lang.definition_helpers import get_definition_by_name, get_definitions_by_root_key
from aac.lang import ActiveContext
from aac.parser import parse
from aac.plugins.validators.defined_references import get_plugin_aac_definitions, register_validators
from aac.plugins.validators.defined_references._validate_references import validate_references
from aac.validate import ValidatorPlugin, ValidationResult

from tests.helpers.parsed_definitions import create_data_definition, create_field_entry


class TestDefinedReferencesPlugin(TestCase):

    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_root_key(parse(get_plugin_aac_definitions()), "validation")
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(name="Type references exist", definition=validation_definitions[0])
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)

    def test_validate_references_valid_references(self):

        test_primitive_reference_field = create_field_entry("ValidPrimitiveField", "string")
        test_definition_reference_field = create_field_entry("ValidBehaviorField", "Behavior")
        test_definition = create_data_definition("Test Definition", [test_primitive_reference_field, test_definition_reference_field])

        expected_result = ValidationResult([], test_definition, True)

        test_active_context = get_active_context(reload_context=True)

        actual_result = validate_references(test_definition, test_active_context)

        self.assertEqual(expected_result, actual_result)

    def test_validate_references_invalid_reference(self):

        invalid_primitive_type = "striiiiing"
        invalid_definition_type = "ThisTypeStringWontAppearInTheCoreSpecIHope"

        test_invalid_primitive_reference_field = create_field_entry("InvalidPrimitiveField", invalid_primitive_type)
        test_invalid_definition_reference_field = create_field_entry("InvalidBehaviorField", invalid_definition_type)
        test_definition = create_data_definition("Test Definition", [test_invalid_primitive_reference_field, test_invalid_definition_reference_field])

        invalid_reference_error_message = ""
        expected_result = ValidationResult([invalid_reference_error_message], test_definition, False)

        test_active_context = get_active_context(reload_context=True)
        # Assert invalid_definition_type is not defined in the active context
        self.assertIsNone(get_definition_by_name(test_active_context.context_definitions, invalid_definition_type))

        # Assert that invalid_primitive_type is not defined in the primitive types
        self.assertIsNone(get_definition_by_name(test_active_context.context_definitions, invalid_definition_type))

        actual_result = validate_references(test_definition, test_active_context)

        self.assertEqual(expected_result, actual_result)
