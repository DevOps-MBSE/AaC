from cgi import test
from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.validate import validated_definitions, validated_source, ValidationError

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_field_entry,
)


class TestValidate(TestCase):
    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_validate_source_with_valid_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_data_definition("Empty Data", [test_field])

        actual_result = None
        with validated_source(test_definition.to_yaml()) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)

    def test_validate_definitions_with_valid_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_data_definition("Empty Data", [test_field])

        actual_result = None
        with validated_definitions([test_definition]) as result:
            actual_result = result

        self.assertTrue(actual_result.is_valid)

    def test_validate_definitions_with_invalid_reference_definition(self):
        test_field = create_field_entry("TestField", "striiiing")
        test_definition = create_data_definition("Empty Data", [test_field])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertGreater(len(exception.args), 1)
        self.assertIn("undefined", exception.args[1].lower())

    def test_validate_definitions_with_invalid_missing_required_field(self):
        test_definition = create_data_definition("Empty Data", [])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([test_definition]):
                pass

        exception = error.exception
        self.assertEqual(ValidationError, type(exception))
        self.assertGreater(len(exception.args), 1)
        self.assertIn("required", exception.args[1].lower())

    def test_multiple_validate_definitions_with_invalid_definition(self):
        invalid_fields_test_field = create_field_entry("MissingTestField")
        del invalid_fields_test_field["type"]
        invalid_reference_test_field = create_field_entry("BadRefTestField", "striiiing")
        invalid_data_definition = create_data_definition("InvalidData", [invalid_fields_test_field, invalid_reference_test_field])

        with self.assertRaises(ValidationError) as error:
            with validated_definitions([invalid_data_definition]):
                pass

        exception = error.exception
        error_messages = "\n".join(exception.args).lower()
        self.assertEqual(ValidationError, type(exception))
        self.assertGreater(len(exception.args), 2)
        self.assertIn("undefined", error_messages)
        self.assertIn("missing", error_messages)
