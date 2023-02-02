from unittest.mock import MagicMock, patch
from aac.validate._validate import _validate_definitions

from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    DEFINITION_FIELD_EXTENSION_ENUM,
    DEFINITION_FIELD_TYPE,
    DEFINITION_NAME_PRIMITIVES,
    DEFINITION_NAME_ROOT,
    PRIMITIVE_TYPE_STRING,
    ROOT_KEY_EXTENSION,
)
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.validators._validator_result import ValidatorFindings, ValidatorResult
from aac.validate import ValidationError, validated_definitions, validated_source
from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_enum_ext_definition,
    create_field_entry,
    create_schema_definition,
    create_schema_ext_definition,
)
from tests.helpers.prebuilt_definition_constants import (
    ALL_PRIMITIVES_INSTANCE,
    ALL_PRIMITIVES_TEST_DEFINITION,
    ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT,
)


class TestValidate(ActiveContextTestCase):
    """TestSuite focused on basic testing of the validate function."""

    def test_validate_source_with_valid_definition(self):
        test_field = create_field_entry("TestField", PRIMITIVE_TYPE_STRING)
        test_definition = create_schema_definition("Test", fields=[test_field])

        actual_result = None
        with validated_source(test_definition.to_yaml()) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)

    def test_validate_definitions_with_valid_definition(self):
        test_field = create_field_entry("TestField", PRIMITIVE_TYPE_STRING)
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

    def test_multiple_validate_definitions_with_invalid_definition(self):
        invalid_fields_test_field = create_field_entry("MissingTestField")
        del invalid_fields_test_field[DEFINITION_FIELD_TYPE]
        invalid_reference_test_field = create_field_entry("BadRefTestField", "striiiing")
        invalid_schema_definition = create_schema_definition(
            "InvalidData", fields=[invalid_fields_test_field, invalid_reference_test_field]
        )

        fake_root_key = "not_a_root_key"
        invalid_root_key_definition = create_schema_definition("Test")
        invalid_root_key_definition.structure[fake_root_key] = invalid_root_key_definition.structure[
            invalid_root_key_definition.get_root_key()
        ]
        del invalid_root_key_definition.structure[invalid_root_key_definition.get_root_key()]
        invalid_root_key_definition, *_ = parse(invalid_root_key_definition.to_yaml())

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
        lexeme = Lexeme(SourceLocation(0, 0, 0, 0), "", "")
        test_findings.add_info_finding(test_definitions[0], "warning message", "test validator", lexeme)
        test_findings.add_warning_finding(test_definitions[0], "warning message", "test validator", lexeme)

        _validate_definitions_mock.return_value = ValidatorResult(test_definitions, test_findings)

        with validated_definitions(test_definitions) as result:
            self.assertEqual(len(result.findings.get_all_findings()), 2)
            self.assertEqual(len(result.findings.get_info_findings()), 1)
            self.assertEqual(len(result.findings.get_warning_findings()), 1)

            self.assertTrue(result.is_valid())


class TestValidatePlugins(ActiveContextTestCase):
    """TestSuite focused on specifically testing validate with relation to plugins."""

    def test_validate_definitions_with_invalid_multiple_exclusive_fields(self):
        test_field_entry = create_field_entry("TestField", PRIMITIVE_TYPE_STRING)
        test_combined_ext_definition = create_schema_ext_definition("TestSchemaExt", "Behavior", fields=[test_field_entry])
        test_enum_definition = create_enum_ext_definition("TestEnumExt", DEFINITION_NAME_PRIMITIVES, values=["val1", "val2"])
        test_combined_ext_definition.structure[ROOT_KEY_EXTENSION][
            DEFINITION_FIELD_EXTENSION_ENUM
        ] = test_enum_definition.structure[ROOT_KEY_EXTENSION][DEFINITION_FIELD_EXTENSION_ENUM]
        test_combined_ext_definition, *_ = parse(test_combined_ext_definition.to_yaml())

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_combined_ext_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertEqual(len(exception.args), 1)
        self.assertIn("multiple", exception.args[0].lower())

    def test_validator_plugin_exception_handling_definition_validation(self):
        def _throw_exception(*args):
            """The exception-throwing function validators."""
            raise RuntimeError("Validator exception.")

        active_context = get_active_context()
        active_validations = [definition.get_validations() for definition in active_context.definitions]
        active_validations = [validation for validation in active_validations if validation and len(validation) > 0]
        active_validation_names = [validation.get("name") for validations in active_validations for validation in validations]
        definition_validations = [
            validation
            for validation in active_context.get_definition_validations()
            if validation.name in active_validation_names
        ]
        self.assertGreater(len(definition_validations), 0)

        for plugin in definition_validations:
            plugin.validation_function = _throw_exception

        validation_result = _validate_definitions([], active_context, True)
        self.assertGreater(len(validation_result.findings.findings), 0)
        findings_message = "\n".join([finding.message for finding in validation_result.findings.findings])

        for plugin in definition_validations:
            self.assertIn(plugin.name, findings_message)

    def test_validator_plugin_exception_handling_primitive_validation(self):
        def _throw_exception(*args):
            """The exception-throwing function validators."""
            raise RuntimeError("Validator exception.")

        active_context = get_active_context()
        active_context.add_definitions_to_context([ALL_PRIMITIVES_TEST_DEFINITION, ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT])
        primitive_validations = active_context.get_primitive_validations()
        self.assertGreater(len(primitive_validations), 0)

        for plugin in primitive_validations:
            plugin.validation_function = _throw_exception

        validation_result = _validate_definitions([ALL_PRIMITIVES_INSTANCE], active_context, False)
        self.assertGreater(len(validation_result.findings.findings), 0)
        findings_message = "\n".join([finding.message for finding in validation_result.findings.findings])

        for plugin in primitive_validations:
            self.assertIn(plugin.name, findings_message)


class TestValidateExtensions(ActiveContextTestCase):
    """TestSuite focused on specifically testing validate with relation to extensions."""

    def test_validate_definitions_with_invalid_root_extension(self):
        invalid_type = "InvalidType"
        invalid_extension_field = create_field_entry("new_root", invalid_type)
        invalid_root_extension = create_schema_ext_definition(
            "NewRoot", DEFINITION_NAME_ROOT, fields=[invalid_extension_field]
        )

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([invalid_root_extension]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertEqual(len(exception.args), 1)
        self.assertIn("undefined", exception.args[0].lower())
        self.assertIn(invalid_type, exception.args[0])

    def test_validate_definitions_with_invalid_target_extension(self):
        invalid_extension_field = create_field_entry("new_field", PRIMITIVE_TYPE_STRING)
        invalid_target = f"{DEFINITION_NAME_ROOT}inTootin"
        invalid_target_extension = create_schema_ext_definition("NewTarget", invalid_target, fields=[invalid_extension_field])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([invalid_target_extension]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertEqual(len(exception.args), 1)
        self.assertIn("undefined", exception.args[0].lower())
        self.assertIn(invalid_target, exception.args[0])
