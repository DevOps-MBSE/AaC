from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus
from aac.context.language_error import LanguageError


from aac.plugins.aac_primitives.aac_primitive_constraints_impl import plugin_name


from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_bool
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_date
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_directory
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_file
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_string
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_int
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_number
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_dataref
from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_typeref


class TestAaCPrimitiveConstraints(TestCase):

    def test_check_bool(self):
        result = check_bool(True, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, "Check bool should return success for a valid bool value of 'true'")
        result = check_bool(False, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, "Check bool should return success for a valid bool value of 'false'")
        result = check_bool("Not_A_Bool", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, "Check bool should return a constraint failure for a non-bool value of 'Not_A_Bool'")

    def test_check_date(self):
        # Test valid date
        result = check_date("2022-01-01", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check date should return success for a valid date value of '2022-01-01'")

        # Test invalid date format
        result = check_date("01-01-2022", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check date should return a constraint failure for an invalid date format of '01-01-2022'")

        # Test invalid date value
        result = check_date("2022-02-31", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check date should return a constraint failure for an invalid date value of '2022-02-31'")

        # Test invalid date type
        result = check_date(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check date should return a constraint failure for an invalid date type of '123'")

    def test_check_directory(self):
        # Test valid directory
        result = check_directory("/path/to/directory", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check directory should return success for a valid directory path of '/path/to/directory'")

        # Test invalid directory path
        result = check_directory("/path/with+/bad\characters|in/directory", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check directory should return a constraint failure for a nonexistent directory path of '/path/with+/bad\characters|in/directory'")

        # Test invalid directory type
        result = check_directory(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check directory should return a constraint failure for an invalid directory type of '123'")

    def test_check_file(self):
        # Test valid linux directory and file name
        result = check_file("/path/to/directory/my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check file should return success for a valid directory path and file name of '/path/to/directory/my_file.txt'")

        # Test valid windows directory and file name
        result = check_file("c:\\path\\to\\directory\\my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check file should return success for a valid directory path and file name of 'c:\path\\to\directory\my_file.txt'")

        # Test valid relative path and file name
        result = check_file("./path/to/directory/my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check file should return success for a valid directory path and file name of './path/to/directory/my_file.txt'")

        # Test valid relative path and file name
        result = check_file("../path/to/directory/my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check file should return success for a valid directory path and file name of '../path/to/directory/my_file.txt'")

        # Test weird but valid relative path and file name
        result = check_file("../path/to/../directory/my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check file should return success for a valid directory path and file name of '../path/to/../directory/my_file.txt'")

        # Test weird but valid relative path and file name
        result = check_file("my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check file should return success for a valid file only of 'my_file.txt'")

        # Test invalid directory path
        result = check_file("/path/with+/bad\characters|in/directory/my_file.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check file should return a constraint failure for a nonexistent directory path of '/path/with+/bad\characters|in/directory/my_file.txt'")

        # Test invalid directory path
        result = check_file("/path/with/bad/characters/in/file/name/m+y|f*ile.txt", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check file should return a constraint failure for a nonexistent directory path of '/path/with/bad/characters/in/file/name/m+y|f*ile.txt'")

        # Test invalid directory type
        result = check_directory(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check file should return a constraint failure for an invalid directory type of '123'")

    def test_check_string(self):
        # Test valid string
        result = check_string("This is a valid string", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check string should return success for a valid string value of 'This is a valid string'")

        # Test invalid string type
        result = check_string(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check string should return a constraint failure for an invalid string type of '123'")

    def test_check_int(self):
        # Test valid integer
        result = check_int(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check int should return success for a valid integer value of '123'")

        # Test valid integer string
        result = check_int("123", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check int should return success for an string integer value of '123'")

        # Test invalid integer value
        result = check_int("abc", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check int should return a constraint failure for an invalid integer value of 'abc'")

    def test_check_number(self):
        # Test valid integer
        result = check_number(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check number should return success for a valid integer value of '123'")

        # Test valid float
        result = check_number(3.14, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check number should return success for a valid float value of '3.14'")

        # Test valid string integer
        result = check_number("123", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check number should return success for a string integer value of '123'")

        # Test valid string float
        result = check_number("3.14", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check number should return success for a string float value of '3.14'")

        # Test invalid number value
        result = check_number("abc", "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check number should return a constraint failure for an invalid number value of 'abc'")

        # Test invalid number type
        result = check_number([1, 2, 3], "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check number should return a constraint failure for an invalid number type of '[1, 2, 3]'")

    def test_check_dataref(self):
        # Test valid dataref
        result = check_dataref("description", "dataref(schema.fields.name)", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check dataref should return success for a valid dataref value of 'description' for field 'schema.fields.name'")

        # Test invalid dataref, bad field chain
        result = check_dataref("description", "dataref(schema.not_a_thing.name)", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check dataref should return a constraint failure for an invalid dataref field chain of 'schema.not_a_thing.name'")

        # Test invalid dataref, bad target value
        result = check_dataref("not_a_field_name_that_exists", "dataref(schema.fields.name)", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check dataref should return a constraint failure for an invalid dataref target value of 'not_a_field_name_that_exists'")

        # Test invalid dataref type
        result = check_dataref(123, "", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check dataref should return a constraint failure for an invalid dataref type of '123'")

    def test_check_typeref(self):
         # Test valid typeref
        result = check_typeref("Schema", "typeref(aac.lang.AacType)", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.SUCCESS, f"{plugin_name}: Check typeref should return success for a valid typeref value of 'Schema' for type 'aac.lang.AacType'")

        # Test invalid typeref value
        result = check_typeref("Not_A_Thing", "typeref(aac.lang.AacType)", None, None)
        self.assertEqual(result.status_code, ExecutionStatus.CONSTRAINT_FAILURE, f"{plugin_name}: Check typeref should return a constraint failure for a invalid valid typeref value of 'Not_A_Thing' for type 'aac.lang.AacType'")

        # Test invalid typeref target type
        with self.assertRaises(LanguageError, msg=f"{plugin_name}: Check typeref should return a constraint failure for a invalid valid typeref type 'not.a.valid.type'"):
            result = check_typeref("Schema", "typeref(not.a.valid.type)", None, None)
        
