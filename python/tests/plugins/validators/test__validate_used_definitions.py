from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_FIELD_NAME, DEFINITION_NAME_SCHEMA
from aac.lang.definitions.collections import get_definition_by_name, get_definitions_by_root_key
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.validators import FindingLocation
from aac.plugins.validators.unused_definitions import validate_used_definitions

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_validator_result_failure, assert_validator_result_success
from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import create_schema_definition, create_enum_definition


class TestValidateUsedDefinitions(ActiveContextTestCase):
    def test_validate_references_valid_references(self):
        test_primitive_reference_field = create_field_entry("ValidPrimitiveField", "string")
        test_definition = create_schema_definition("TestData", fields=[test_primitive_reference_field])

        expected_result = ValidatorResult()

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_definition)
        target_schema_definition = get_definition_by_name("Field", test_active_context.definitions)

        actual_result = validate_used_definitions(test_definition, target_schema_definition, test_active_context)

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

        actual_result = validate_used_definitions(test_invalid_schema_definition, field_definition, test_active_context, "type")
        actual_result_message = actual_result.get_messages_as_string()

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())
        self.assertEqual(expected_finding_location, actual_result.findings.get_error_findings()[0].location.location)
        self.assertIn("Undefined", actual_result_message)
        self.assertIn(invalid_definition_type, actual_result_message)
