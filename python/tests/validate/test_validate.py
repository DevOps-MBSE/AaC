from aac.lang.definitions.definition import Definition
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
        self.assertGreater(len(exception.args), 1)
        self.assertIn("undefined", exception.args[1].lower())

    def test_validate_definitions_with_invalid_missing_required_field(self):
        test_definition = create_schema_definition("Empty Schema", fields=[])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertGreater(len(exception.args), 1)
        self.assertIn("required", exception.args[1].lower())

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
        self.assertGreater(len(exception.args), 1)
        self.assertIn("multiple", exception.args[1].lower())

    def test_multiple_validate_definitions_with_invalid_definition(self):
        invalid_fields_test_field = create_field_entry("MissingTestField")
        del invalid_fields_test_field["type"]
        invalid_reference_test_field = create_field_entry("BadRefTestField", "striiiing")
        invalid_data_definition = create_schema_definition("InvalidData", fields=[invalid_fields_test_field, invalid_reference_test_field])

        fake_root_key = "not_a_root_key"
        test_definition_dict = {
            fake_root_key: {
                "name": "Test",
            }
        }
        invalid_root_key_definition = Definition("Test", "", "", [], test_definition_dict)

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([invalid_data_definition, invalid_root_key_definition]):
                pass

        exception = error.exception
        error_messages = "\n".join(exception.args).lower()
        self.assertEqual(ValidationError, type(exception))
        self.assertGreater(len(exception.args), 2)
        self.assertIn("undefined", error_messages)
        self.assertIn("missing", error_messages)
        self.assertIn("root", error_messages)
        self.assertIn(fake_root_key, error_messages)
