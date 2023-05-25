from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definition_by_name, get_definitions_by_root_key
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution
from aac.plugins.validators import ValidatorFindings, ValidatorResult
from aac.plugins.validators.defined_references import _get_plugin_definitions, _get_plugin_validations, validate_references
from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_definitions_equal
from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import create_field_entry, create_schema_definition


class TestDefinedReferencesPlugin(ActiveContextTestCase):
    def test_module_register_validators(self):
        actual_validator_plugins = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key("validation", _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        validation_definition = validation_definitions[0]
        expected_definition_validation = DefinitionValidationContribution(
            name=validation_definition.name, definition=validation_definition, validation_function=(lambda x: x)
        )
        self.assertEqual(expected_definition_validation.name, actual_validator_plugins[0].name)
        assert_definitions_equal(expected_definition_validation.definition, actual_validator_plugins[0].definition)

    def test_validate_references_valid_references(self):
        test_primitive_reference_field = create_field_entry("ValidPrimitiveField", "string")
        test_definition = create_schema_definition("TestData", fields=[test_primitive_reference_field])

        expected_result = ValidatorResult()

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_definition)
        target_schema_definition = get_definition_by_name("Field", test_active_context.definitions)

        actual_result = validate_references(test_definition, target_schema_definition, test_active_context)

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())

    def test_validate_references_invalid_definition_reference(self):
        invalid_definition_type = "ThisTypeStringWontAppearInTheCoreSpecIHope"

        test_invalid_definition_reference_field = create_field_entry("InvalidBehaviorField", invalid_definition_type)
        test_invalid_schema_definition = create_schema_definition(
            "InvalidSchema", fields=[test_invalid_definition_reference_field]
        )

        invalid_reference_error_message = ""
        test_findings = ValidatorFindings()
        expected_finding_location = SourceLocation(4, 10, 81, 42)
        lexeme = Lexeme(expected_finding_location, "", "")
        test_findings.add_error_finding(
            test_invalid_schema_definition, invalid_reference_error_message, "validate thing", lexeme
        )
        expected_result = ValidatorResult([test_invalid_schema_definition], test_findings)

        test_active_context = get_core_spec_context([test_invalid_schema_definition])
        field_definition = test_active_context.get_definition_by_name("Field")

        actual_result = validate_references(test_invalid_schema_definition, field_definition, test_active_context, "type")
        actual_result_message = actual_result.get_messages_as_string()

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())
        self.assertEqual(expected_finding_location, actual_result.findings.get_error_findings()[0].location.location)
        self.assertIn("Undefined", actual_result_message)
        self.assertIn(invalid_definition_type, actual_result_message)

    def test_validate_references_invalid_primitive_reference(self):
        invalid_primitive_type = "striiiiing"

        test_invalid_primitive_reference_field = create_field_entry("InvalidPrimitiveField", invalid_primitive_type)
        test_invalid_schema_definition = create_schema_definition(
            "InvalidSchema", fields=[test_invalid_primitive_reference_field]
        )

        invalid_reference_error_message = ""
        expected_findings = ValidatorFindings()
        expected_finding_location = SourceLocation(4, 10, 82, 10)
        lexeme = Lexeme(expected_finding_location, "", "")
        expected_findings.add_error_finding(
            test_invalid_schema_definition, invalid_reference_error_message, "validate thing", lexeme
        )
        expected_result = ValidatorResult([test_invalid_schema_definition], expected_findings)

        test_active_context = get_core_spec_context([test_invalid_schema_definition])
        field_definition = test_active_context.get_definition_by_name("Field")

        actual_result = validate_references(test_invalid_schema_definition, field_definition, test_active_context, "type")
        actual_result_message = actual_result.get_messages_as_string()

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())
        self.assertEqual(expected_finding_location, actual_result.findings.get_error_findings()[0].location.location)
        self.assertIn("Undefined", actual_result_message)
        self.assertIn(invalid_primitive_type, actual_result_message)
