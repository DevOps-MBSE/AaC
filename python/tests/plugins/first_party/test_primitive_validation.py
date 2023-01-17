from aac.lang.active_context_lifecycle_manager import get_active_context

from aac.validate import validated_source
from aac.io.constants import DEFINITION_SEPARATOR
from aac.plugins.first_party.primitive_type_check.validators import int_validator
from aac.plugins.first_party.primitive_type_check.validators import bool_validator
from aac.plugins.first_party.primitive_type_check.validators import num_validator

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_validator_result_success
from tests.helpers.io import temporary_test_file
from tests.helpers.parsed_definitions import create_definition
from tests.helpers.prebuilt_definition_constants import (
    TEST_TYPES_SCHEMA_DEFINITION,
    TEST_TYPES_SCHEMA_EXTENSION_DEFINITION,
    TEST_TYPES_VALID_INSTANCE,
    TEST_TYPES_INVALID_INSTANCE,
    TEST_TYPES_ROOT_KEY,
    SCHEMA_FIELD_INT,
    SCHEMA_FIELD_BOOL,
    SCHEMA_FIELD_NUMBER,
)


class TestPrimitiveValidation(ActiveContextTestCase):

    INTEGER_VALIDATOR = int_validator.get_validator()
    BOOLEAN_VALIDATOR = bool_validator.get_validator()
    NUMBER_VALIDATOR = num_validator.get_validator()

    VALID_PRIMITIVES_FILE_CONTENT = DEFINITION_SEPARATOR.join(
        [
            TEST_TYPES_SCHEMA_DEFINITION.to_yaml(),
            TEST_TYPES_SCHEMA_EXTENSION_DEFINITION.to_yaml(),
            TEST_TYPES_VALID_INSTANCE.to_yaml(),
        ]
    )

    INVALID_PRIMITIVES_FILE_CONTENT = DEFINITION_SEPARATOR.join(
        [
            TEST_TYPES_SCHEMA_DEFINITION.to_yaml(),
            TEST_TYPES_SCHEMA_EXTENSION_DEFINITION.to_yaml(),
            TEST_TYPES_INVALID_INSTANCE.to_yaml(),
        ]
    )

    def test_type_check_valid(self):
        with (
            temporary_test_file(self.VALID_PRIMITIVES_FILE_CONTENT) as test_file,
            validated_source(test_file.name) as result,
        ):
            get_active_context().add_definitions_to_context(result.definitions)
            assert_validator_result_success(result)

    def test_type_check_invalid(self):
        with (
            temporary_test_file(self.INVALID_PRIMITIVES_FILE_CONTENT) as test_file,
            self.assertRaises(Exception) as error,
            validated_source(test_file.name),
        ):

            self.assertIsNotNone(error.exception)

            self.assertIn(self.INTEGER_VALIDATOR.name, error.exception)
            self.assertIn(self.INTEGER_VALIDATOR.primitive_type, error.exception)
            self.assertIn(self.BOOLEAN_VALIDATOR.name, error.exception)
            self.assertIn(self.BOOLEAN_VALIDATOR.primitive_type, error.exception)
            self.assertIn(self.NUMBER_VALIDATOR.primitive_type, error.exception)

    def test_integer_type_check_valid(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.INTEGER_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, 0)
        self.assertIsNone(finding)

    def test_integer_type_check_invalid_float(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        invalid_int_value = 0.5
        invalid_definition = create_definition(
            TEST_TYPES_ROOT_KEY, "invalidPrimitives", {SCHEMA_FIELD_INT.get("name"): invalid_int_value}
        )

        finding = self.INTEGER_VALIDATOR.validation_function(invalid_definition, invalid_int_value)
        self.assertIsNotNone(finding)

    def test_integer_type_check_invalid_string(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        invalid_int_value = "DefinitelyNotAnInt"
        invalid_definition = create_definition(
            TEST_TYPES_ROOT_KEY, "invalidPrimitives", {SCHEMA_FIELD_INT.get("name"): invalid_int_value}
        )

        finding = self.INTEGER_VALIDATOR.validation_function(invalid_definition, invalid_int_value)
        self.assertIsNotNone(finding)

    def test_boolean_type_valid_true(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.BOOLEAN_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, True)
        self.assertIsNone(finding)

    def test_boolean_type_valid_false(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.BOOLEAN_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, False)
        self.assertIsNone(finding)

    def test_boolean_type_invalid(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        invalid_bool_value = "WhipperSnapper"
        invalid_definition = create_definition(
            TEST_TYPES_ROOT_KEY, "booleanType", {SCHEMA_FIELD_BOOL.get("name"): invalid_bool_value}
        )

        finding = self.BOOLEAN_VALIDATOR.validation_function(invalid_definition, invalid_bool_value)
        self.assertIsNotNone(finding)

    def test_number_type_valid_octal(self):
        test_context = get_active_context()
        test_context.add_definition_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.NUMBER_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, "0o14")
        self.assertIsNone(finding)

    def test_number_type_valid_hexadec(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.NUMBER_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, "0xC")
        self.assertIsNone(finding)

    def test_number_type_valid_float(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.NUMBER_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, 13.4)
        self.assertIsNone(finding)

    def test_number_type_valid_exponential(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.NUMBER_VALIDATOR.validation_function(TEST_TYPES_INVALID_INSTANCE, 1.2e+34)
        self.assertIsNone(finding)

    def test_number_type_valid_inf(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        finding = self.NUMBER_VALIDATOR.validation_function(TEST_TYPES_VALID_INSTANCE, '.inf')
        self.assertIsNone(finding)

    def test_number_type_invalid(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        invalid_numb_value = "ThisIsDefNotANumber"
        invalid_definition = create_definition(
            TEST_TYPES_ROOT_KEY, "numberType", {SCHEMA_FIELD_NUMBER.get("name"): invalid_numb_value}
        )

        finding = self.BOOLEAN_VALIDATOR.validation_function(invalid_definition, invalid_numb_value)
        self.assertIsNotNone(finding)
