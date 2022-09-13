from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name, get_definitions_by_root_key
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.plugins.validators.defined_references import _get_plugin_definitions, _get_plugin_validations, validate_references

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import create_schema_definition, create_field_entry


class TestDefinedReferencesPlugin(ActiveContextTestCase):
    def test_module_register_validators(self):
        actual_validator_plugins = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key("validation", _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        validation_definition = validation_definitions[0]
        expected_validator_plugin = ValidatorPlugin(
            name=validation_definition.name, definition=validation_definition, validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugins[0].name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugins[0].definition)

    def test_validate_references_valid_references(self):
        test_primitive_reference_field = create_field_entry("ValidPrimitiveField", "string")
        test_definition = create_schema_definition("TestData", fields=[test_primitive_reference_field])

        expected_result = ValidatorResult([], True)

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_definition)
        target_schema_definition = get_definition_by_name("Field", test_active_context.definitions)

        actual_result = validate_references(test_definition, target_schema_definition, test_active_context)

        self.assertEqual(expected_result, actual_result)

    def test_validate_references_invalid_definition_reference(self):

        invalid_definition_type = "ThisTypeStringWontAppearInTheCoreSpecIHope"

        test_invalid_definition_reference_field = create_field_entry("InvalidBehaviorField", invalid_definition_type)
        test_invalid_schema_definition = create_schema_definition("InvalidSchema", fields=[test_invalid_definition_reference_field])

        invalid_reference_error_message = ""
        expected_result = ValidatorResult([invalid_reference_error_message], False)

        test_active_context = get_core_spec_context([test_invalid_schema_definition])
        field_definition = test_active_context.get_definition_by_name("Field")

        actual_result = validate_references(test_invalid_schema_definition, field_definition, test_active_context, 'type')

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertIn("Undefined", "\n".join(actual_result.messages))
        self.assertIn(invalid_definition_type, "\n".join(actual_result.messages))

    def test_validate_references_invalid_primitive_reference(self):

        invalid_primitive_type = "striiiiing"

        test_invalid_primitive_reference_field = create_field_entry("InvalidPrimitiveField", invalid_primitive_type)
        test_invalid_schema_definition = create_schema_definition("InvalidSchema", fields=[test_invalid_primitive_reference_field])

        invalid_reference_error_message = ""
        expected_result = ValidatorResult([invalid_reference_error_message], False)

        test_active_context = get_core_spec_context([test_invalid_schema_definition])
        field_definition = test_active_context.get_definition_by_name("Field")

        actual_result = validate_references(test_invalid_schema_definition, field_definition, test_active_context, 'type')

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertIn("Undefined", "\n".join(actual_result.messages))
        self.assertIn(invalid_primitive_type, "\n".join(actual_result.messages))
