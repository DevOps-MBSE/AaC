from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name, get_definitions_by_root_key
from aac.parser import parse
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.plugins.validators.defined_references import get_plugin_aac_definitions, register_validators, validate_references
from tests.helpers.context import get_core_spec_context

from tests.helpers.parsed_definitions import create_schema_definition, create_field_entry


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
        test_definition = create_schema_definition("TestData", [test_primitive_reference_field])

        expected_result = ValidatorResult([], True)

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_definition)
        target_schema_definition = get_definition_by_name("Field", test_active_context.definitions)

        actual_result = validate_references(test_definition, target_schema_definition, test_active_context)

        self.assertEqual(expected_result, actual_result)

    def test_validate_references_invalid_definition_reference(self):

        invalid_definition_type = "ThisTypeStringWontAppearInTheCoreSpecIHope"

        test_invalid_definition_reference_field = create_field_entry("InvalidBehaviorField", invalid_definition_type)
        test_invalid_data_defintion = create_schema_definition("InvalidData", fields=[test_invalid_definition_reference_field])

        invalid_reference_error_message = ""
        expected_result = ValidatorResult([invalid_reference_error_message], False)

        test_active_context = get_core_spec_context([test_invalid_data_defintion])
        field_definition = test_active_context.get_definition_by_name("Field")

        actual_result = validate_references(test_invalid_data_defintion, field_definition, test_active_context)

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertIn("Undefined", "\n".join(actual_result.messages))
        self.assertIn(invalid_definition_type, "\n".join(actual_result.messages))

    def test_validate_references_invalid_primitive_reference(self):

        invalid_primitive_type = "striiiiing"

        test_invalid_primitive_reference_field = create_field_entry("InvalidPrimitiveField", invalid_primitive_type)
        test_invalid_data_defintion = create_schema_definition("InvalidData", fields=[test_invalid_primitive_reference_field])

        invalid_reference_error_message = ""
        expected_result = ValidatorResult([invalid_reference_error_message], False)

        test_active_context = get_core_spec_context([test_invalid_data_defintion])
        field_definition = test_active_context.get_definition_by_name("Field")

        actual_result = validate_references(test_invalid_data_defintion, field_definition, test_active_context)

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertIn("Undefined", "\n".join(actual_result.messages))
        self.assertIn(invalid_primitive_type, "\n".join(actual_result.messages))
