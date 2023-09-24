from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.validators import ValidatorFindings, ValidatorResult
from aac.plugins.validators.unused_definitions import validate_used_definitions

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import create_schema_definition, create_field_entry


class TestValidateUsedDefinitions(ActiveContextTestCase):
    def test_validate_references_valid_definition_reference(self):
        test_valid_definition_field = create_field_entry("ValidDefinitionField", "string")
        test_definition = create_schema_definition("TestData", fields=[test_valid_definition_field])

        expected_result = ValidatorResult()

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definition_to_context(test_definition)
        target_schema_definition = get_definition_by_name("Field", test_active_context.definitions)

        actual_result = validate_used_definitions(test_definition, target_schema_definition, test_active_context)

        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())

    def test_validate_references_invalid_definition_reference(self):
        test_unreferenced_schema_definition = create_schema_definition(
            "UnreferencedSchema", fields=[]
        )
        invalid_reference_error_message = ""
        
        test_findings = ValidatorFindings()
        expected_finding_location = SourceLocation(1, 8, 16, 18)
        lexeme = Lexeme(expected_finding_location, "", "")
        test_findings.add_info_finding(
            test_unreferenced_schema_definition, invalid_reference_error_message, "validate thing", lexeme
        )
        expected_result = ValidatorResult([test_unreferenced_schema_definition], test_findings)
        
        test_active_context = get_core_spec_context([test_unreferenced_schema_definition])
        field_definition = test_active_context.get_definition_by_name("Field")
        
        actual_result = validate_used_definitions(test_unreferenced_schema_definition, field_definition, test_active_context, "type")
        actual_result_message = actual_result.get_messages_as_string()
        
        self.assertEqual(expected_result.is_valid(), actual_result.is_valid())
        self.assertEqual(expected_finding_location, actual_result.findings.get_info_findings()[0].location.location)
        self.assertIn("No references", actual_result_message)
        self.assertIn(test_unreferenced_schema_definition.name, actual_result_message)
