from os import remove, removedirs
from os.path import lexists
from tempfile import TemporaryDirectory
from typing import Optional

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.io.constants import DEFINITION_SEPARATOR
from aac.io.parser import parse
from aac.lang.constants import DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_BOOL, PRIMITIVE_TYPE_DATE, PRIMITIVE_TYPE_FILE, PRIMITIVE_TYPE_INT, PRIMITIVE_TYPE_NUMBER
from aac.plugins.first_party.primitive_type_check.validators import (
    bool_validator,
    file_validator,
    int_validator,
    num_validator,
    date_validator,
)
from aac.plugins.validators import ValidatorFinding, FindingSeverity
from aac.validate import validated_source

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_validator_result_success
from tests.helpers.io import temporary_test_file, temporary_test_file_wo_cm
from tests.helpers.parsed_definitions import create_definition, NAME_STRING
from tests.helpers.prebuilt_definition_constants import (
    ALL_PRIMITIVES_INSTANCE,
    ALL_PRIMITIVES_TEST_DEFINITION,
    ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT,
    TEST_TYPES_SCHEMA_DEFINITION,
    TEST_TYPES_SCHEMA_EXTENSION_DEFINITION,
    TEST_TYPES_ROOT_KEY,
    SCHEMA_FIELD_INT,
    SCHEMA_FIELD_BOOL,
    SCHEMA_FIELD_FILE,
    get_primitive_definition_values,
)


class TestPrimitiveValidation(ActiveContextTestCase):
    INTEGER_VALIDATOR = int_validator.get_validator()
    BOOLEAN_VALIDATOR = bool_validator.get_validator()
    NUMBER_VALIDATOR = num_validator.get_validator()
    FILE_VALIDATOR = file_validator.get_validator()
    DATE_VALIDATOR = date_validator.get_validator()

    def setUp(self) -> None:
        super().setUp()

        self.TEST_DIRECTORY = TemporaryDirectory()
        self.TEST_FILE = temporary_test_file_wo_cm("", dir=self.TEST_DIRECTORY.name)

        self.TEST_TYPES_VALID_INSTANCE = create_definition(
            TEST_TYPES_ROOT_KEY, "validPrimitives", get_primitive_definition_values(0, True, self.TEST_FILE.name, 0.0, None)
        )
        self.VALID_PRIMITIVES_FILE_CONTENT = DEFINITION_SEPARATOR.join(
            [
                TEST_TYPES_SCHEMA_DEFINITION.to_yaml(),
                TEST_TYPES_SCHEMA_EXTENSION_DEFINITION.to_yaml(),
                self.TEST_TYPES_VALID_INSTANCE.to_yaml(),
            ]
        )

        self.TEST_TYPES_INVALID_INSTANCE = create_definition(
            TEST_TYPES_ROOT_KEY,
            "invalidPrimitives",
            get_primitive_definition_values(0.5, "maybe", "/does/not/exist", 0.0, None),
        )
        self.INVALID_PRIMITIVES_FILE_CONTENT = DEFINITION_SEPARATOR.join(
            [
                TEST_TYPES_SCHEMA_DEFINITION.to_yaml(),
                TEST_TYPES_SCHEMA_EXTENSION_DEFINITION.to_yaml(),
                self.TEST_TYPES_INVALID_INSTANCE.to_yaml(),
            ]
        )

    def tearDown(self) -> None:
        super().tearDown()

        if lexists(self.TEST_FILE.name):
            remove(self.TEST_FILE.name)
            removedirs(self.TEST_DIRECTORY.name)

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

            exception_message = str(error.exception)
            self.assertIn(self.INTEGER_VALIDATOR.name, exception_message)
            self.assertIn(self.INTEGER_VALIDATOR.primitive_type, exception_message)
            self.assertIn(self.BOOLEAN_VALIDATOR.name, exception_message)
            self.assertIn(self.BOOLEAN_VALIDATOR.primitive_type, exception_message)
            self.assertIn(self.NUMBER_VALIDATOR.name, exception_message)
            self.assertIn(self.NUMBER_VALIDATOR.primitive_type, exception_message)
            self.assertIn(self.FILE_VALIDATOR.name, exception_message)
            self.assertIn(self.FILE_VALIDATOR.primitive_type, exception_message)

    def test_integer_type_valid(self):
        valid_int = ["10", "012345678", "999999999999999999"]
        self._test_valid_primitive_validation(PRIMITIVE_TYPE_INT, "0", valid_int)

    def test_integer_type_invalid(self):
        finding_assertion = f".*not.*valid.*type.*{PRIMITIVE_TYPE_INT}"
        invalid_int = ["0.0", ".inf", "10e2", "-1293"]
        self._test_invalid_primitive_validation(PRIMITIVE_TYPE_INT, "0", invalid_int, finding_assertion)

    def test_boolean_type_valid(self):
        valid_bool = ["true", "false", "yes", "no", "on", "off"]
        self._test_valid_primitive_validation(PRIMITIVE_TYPE_BOOL, "true", valid_bool)

    def test_boolean_type_invalid(self):
        finding_assertion = f".*not.*valid.*type.*{PRIMITIVE_TYPE_BOOL}"
        invalid_bool = ["Y", "N", "negative"]
        self._test_invalid_primitive_validation(PRIMITIVE_TYPE_BOOL, "true", invalid_bool, finding_assertion)

    def test_number_type_valid_values(self):
        valid_numbers = ["13.4", "1.2e+34", "0x14"]
        self._test_valid_primitive_validation(PRIMITIVE_TYPE_NUMBER, "20.2", valid_numbers)

    def test_number_type_invalid_values(self):
        finding_assertion = f".*not.*valid.*type.*{PRIMITIVE_TYPE_NUMBER}"
        invalid_numbers = ["13.4.7", "1.2e34", "xx14"]
        self._test_invalid_primitive_validation(PRIMITIVE_TYPE_NUMBER, "20.2", invalid_numbers, finding_assertion)

    def test_file_type_valid_file(self):
        with temporary_test_file("") as test_file:
            valid_files = [test_file.name]
            self._test_valid_primitive_validation(PRIMITIVE_TYPE_FILE, "./test.aac", valid_files)

    def test_file_type_invalid_file(self):
        finding_assertion = ".*not.*exist"
        invalid_numbers = ["/i/don't/exist", "https://google.com"]
        self._test_invalid_primitive_validation(PRIMITIVE_TYPE_FILE, "./test.aac", invalid_numbers, finding_assertion)

    def test_file_type_valid(self):
        test_context = get_active_context()
        test_context.add_definitions_to_context([TEST_TYPES_SCHEMA_DEFINITION, TEST_TYPES_SCHEMA_EXTENSION_DEFINITION])

        with temporary_test_file("") as test_file:
            finding = self.FILE_VALIDATOR.validation_function(self.TEST_TYPES_VALID_INSTANCE, test_file.name)
            self.assertIsNone(finding)

    def test_data_type_valid_format(self):
        valid_dates = ["2020-02-08"]
        self._test_valid_primitive_validation(PRIMITIVE_TYPE_DATE, "1970-01-01 00:00:00", valid_dates)

    def test_data_type_invalid_format(self):
        finding_assertion = f".*not.*valid.*{PRIMITIVE_TYPE_DATE}"
        invalid_dates = ["2020-jan:08", "5-06-2020", "1970-01-01TTTT00:00:00Z", "2020T065"]
        self._test_invalid_primitive_validation(PRIMITIVE_TYPE_DATE, "1970-01-01 00:00:00", invalid_dates, finding_assertion)

    def _test_valid_primitive_validation(self, primitive_type: str, default_value: str, test_values: list[str]):
        """Test apparatus for asserting that the primitive validators don't report errors for valid values.

        Args:
            primitive_type (str): The primitive type under test
            default_value (str): The default value of the field, this is the value we'll replace
            test_values: (list[str]): The list of values that will replace default_value
        """
        for valid_value in test_values:
            self._test_primitive_validation(
                primitive_type,
                default_value,
                valid_value,
                f"Failed to validate good {primitive_type}: '{valid_value}'",
                self.assertIsNone,
            )

    def _test_invalid_primitive_validation(self, primitive_type: str, default_value: str, test_values: list[str], finding_regex_assertion: str):
        """Test apparatus for asserting that the primitive validators do report errors for invalid values.

        Args:
            primitive_type (str): The primitive type under test
            default_value (str): The default value of the field, this is the value we'll replace
            test_values: (list[str]): The list of values that will replace default_value
            finding_regex_assertion (str): A regex string used to assert that expected components are present in the message
        """
        for valid_value in test_values:
            self._test_primitive_validation(
                primitive_type,
                default_value,
                valid_value,
                f"Failed to identify bad {primitive_type}: '{valid_value}'",
                self.assertIsNotNone,
                finding_regex_assertion
            )

    def _test_primitive_validation(
        self,
        primitive_type: str,
        default_value: str,
        test_value: str,
        assertion_error: str,
        assertion_function: callable,
        finding_regex_assertion: str = ""
    ) -> Optional[ValidatorFinding]:
        validators_lookup = {
            PRIMITIVE_TYPE_DATE: self.DATE_VALIDATOR,
            PRIMITIVE_TYPE_NUMBER: self.NUMBER_VALIDATOR,
            PRIMITIVE_TYPE_INT: self.INTEGER_VALIDATOR,
            PRIMITIVE_TYPE_BOOL: self.BOOLEAN_VALIDATOR,
            PRIMITIVE_TYPE_FILE: self.FILE_VALIDATOR,
        }

        test_context = get_active_context()
        test_context.add_definitions_to_context(
            [ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT, ALL_PRIMITIVES_TEST_DEFINITION]
        )
        test_definition_yaml = ALL_PRIMITIVES_INSTANCE.to_yaml()
        test_definition_yaml = test_definition_yaml.replace(default_value, test_value)
        self.assertIn(test_value, test_definition_yaml)

        # Re-parse the definition so that we can give it a lexeme for the new value.
        test_definition, *_ = parse(test_definition_yaml, ALL_PRIMITIVES_INSTANCE.source.uri)

        # Assert that the number validator will not return a finding because the float value is valid.
        self.assertIn(primitive_type, validators_lookup)
        finding = validators_lookup.get(primitive_type).validation_function(
            test_definition, test_definition.structure[test_definition.get_root_key()][primitive_type.upper()]
        )

        assertion_function(finding, assertion_error)
        if finding_regex_assertion:
            self.assertRegexpMatches(finding.message, finding_regex_assertion)
