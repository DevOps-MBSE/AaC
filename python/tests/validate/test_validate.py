from unittest.mock import MagicMock, patch

from aac.io.files.aac_file import AaCFile
from aac.lang.definitions.definition import Definition
from aac.plugins.validators._validator_result import ValidatorResult, ValidatorFindings
from aac.validate import validated_definitions, validated_source, ValidationError

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestValidate(ActiveContextTestCase):
    def test_validate_source_with_valid_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_schema_definition("Test", fields=[test_field])

        actual_result = None
        with validated_source(test_definition.to_yaml()) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)

    def test_validate_definitions_with_valid_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_schema_definition("Test", fields=[test_field])

        actual_result = None
        with validated_definitions([test_definition]) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)

    def test_validate_definitions_with_invalid_reference_definition(self):
        test_field = create_field_entry("TestField", "striiiing")
        test_definition = create_schema_definition("InvalidTest", fields=[test_field])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertEqual(len(exception.args), 1)
        self.assertIn("undefined", exception.args[0].lower())

    def test_validate_definitions_with_invalid_missing_required_field(self):
        test_definition = create_schema_definition("Empty Schema", fields=[])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertEqual(len(exception.args), 1)
        self.assertIn("required", exception.args[0].lower())

    def test_validate_definitions_with_invalid_multiple_exclusive_fields(self):
        test_field_entry = create_field_entry("TestField", "string")
        test_combined_ext_definition = create_schema_ext_definition("TestSchemaExt", "Behavior", fields=[test_field_entry])
        test_enum_definition = create_enum_ext_definition("TestEnumExt", "Primitives", values=["val1", "val2"])
        test_combined_ext_definition.structure["ext"]["enumExt"] = test_enum_definition.structure["ext"]["enumExt"]

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_combined_ext_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertEqual(len(exception.args), 1)
        self.assertIn("multiple", exception.args[0].lower())

    def test_multiple_validate_definitions_with_invalid_definition(self):
        invalid_fields_test_field = create_field_entry("MissingTestField")
        del invalid_fields_test_field["type"]
        invalid_reference_test_field = create_field_entry("BadRefTestField", "striiiing")
        invalid_schema_definition = create_schema_definition("InvalidData", fields=[invalid_fields_test_field, invalid_reference_test_field])

        fake_root_key = "not_a_root_key"
        test_definition_dict = {
            fake_root_key: {
                "name": "Test",
            }
        }
        invalid_definition_source = AaCFile("<test>", True, False)
        invalid_root_key_definition = Definition("Test", "", invalid_definition_source, [], test_definition_dict)

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([invalid_schema_definition, invalid_root_key_definition]):
                pass

        exception = error.exception
        error_messages = "\n".join(exception.args).lower()
        self.assertEqual(ValidationError, type(exception))
        self.assertGreater(error_messages.count("\n"), 3)
        self.assertIn("undefined", error_messages)
        self.assertIn("missing", error_messages)
        self.assertIn("root", error_messages)
        self.assertIn(fake_root_key, error_messages)

    @patch("aac.validate._validate._validate_definitions")
    def test_non_error_findings_do_not_cause_validation_failures(self, _validate_definitions_mock: MagicMock):
        test_definitions = [create_schema_definition("Test")]

        test_findings = ValidatorFindings()
        test_findings.add_info_finding(test_definitions[0], "warning message", "test validator", 0, 0, 0, 0)
        test_findings.add_warning_finding(test_definitions[0], "warning message", "test validator", 0, 0, 0, 0)

        _validate_definitions_mock.return_value = ValidatorResult(test_definitions, test_findings)

        with validated_definitions(test_definitions) as result:
            self.assertEqual(len(result.findings.get_all_findings()), 2)
            self.assertEqual(len(result.findings.get_info_findings()), 1)
            self.assertEqual(len(result.findings.get_warning_findings()), 1)

            self.assertTrue(result.is_valid())
