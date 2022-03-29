from unittest import TestCase

from aac.lang.context_manager import get_active_context
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.parser import parse
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.plugins.validators.defined_references import get_plugin_aac_definitions, register_validators, validate_references

from tests.helpers.parsed_definitions import create_field_entry


class TestDefinedReferencesPlugin(TestCase):
    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_root_key("validation", parse(get_plugin_aac_definitions()))
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(
            name="Type references exist", definition=validation_definitions[0], validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)

    def test_validate_references_valid_references(self):
        test_primitive_reference_field = create_field_entry("ValidPrimitiveField", "string")

        expected_result = ValidatorResult([], True)

        test_active_context = get_active_context(reload_context=True)

        actual_result = validate_references(test_primitive_reference_field, test_active_context)

        self.assertEqual(expected_result, actual_result)

    def test_validate_references_invalid_definition_reference(self):

        invalid_definition_type = "ThisTypeStringWontAppearInTheCoreSpecIHope"

        test_invalid_definition_reference_field = create_field_entry("InvalidBehaviorField", invalid_definition_type)

        invalid_reference_error_message = ""
        expected_result = ValidatorResult([invalid_reference_error_message], False)

        test_active_context = get_active_context(reload_context=True)

        actual_result = validate_references(test_invalid_definition_reference_field, test_active_context)

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertIn("Undefined", "\n".join(actual_result.messages))
        self.assertIn(invalid_definition_type, "\n".join(actual_result.messages))

    def test_validate_references_invalid_primitive_reference(self):

        invalid_primitive_type = "striiiiing"

        test_invalid_primitive_reference_field = create_field_entry("InvalidPrimitiveField", invalid_primitive_type)

        invalid_reference_error_message = ""
        expected_result = ValidatorResult([invalid_reference_error_message], False)

        test_active_context = get_active_context(reload_context=True)

        actual_result = validate_references(test_invalid_primitive_reference_field, test_active_context)

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertIn("Undefined", "\n".join(actual_result.messages))
        self.assertIn(invalid_primitive_type, "\n".join(actual_result.messages))
