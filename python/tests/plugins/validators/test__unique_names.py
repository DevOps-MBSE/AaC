from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.validators.unique_names._unique_names import validate_unique_names

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_validator_result_failure, assert_validator_result_success
from tests.helpers.parsed_definitions import create_enum_definition, create_schema_definition


class TestValidateUniqueNames(ActiveContextTestCase):
    def test_validation_succeeds_with_no_definitions(self):
        new_definition = create_schema_definition("New")
        actual_result = validate_unique_names(new_definition, new_definition, get_active_context())

        assert_validator_result_success(actual_result)

    def test_validation_succeeds_with_no_duplicated_names(self):
        test_active_context = get_active_context()
        test_active_context.add_definitions_to_context([create_schema_definition(f"Test{i}") for i in range(1, 100)])

        new_definition = create_schema_definition("Test0")
        unused_definition = create_schema_definition("unused")
        actual_result = validate_unique_names(new_definition, unused_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validation_succeeds_with_no_duplicated_names_of_different_types(self):
        test_active_context = get_active_context()

        definition = create_schema_definition("Test1")
        test_active_context.add_definition_to_context(definition)

        new_definition = create_enum_definition("Test2", ["a", "b", "c"])
        unused_definition = create_schema_definition("unused")
        actual_result = validate_unique_names(new_definition, unused_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validation_fails_with_duplicated_names_of_same_type(self):
        test_active_context = get_active_context()
        test_active_context.add_definitions_to_context(parse(TEST_CONTENT, __file__))

        new_definition = create_schema_definition("Test1")
        unused_definition = create_schema_definition("unused")
        actual_result = validate_unique_names(new_definition, unused_definition, test_active_context)

        assert_validator_result_failure(actual_result)

    def test_validation_fails_with_duplicated_names_of_different_types(self):
        test_active_context = get_active_context()

        definition = create_schema_definition("Test")
        test_active_context.add_definition_to_context(definition)

        new_definition = create_enum_definition("Test", ["a", "b", "c"])
        unused_definition = create_schema_definition("unused")
        actual_result = validate_unique_names(new_definition, unused_definition, test_active_context)

        assert_validator_result_failure(actual_result)

    def test_validation_fails_with_duplicated_name_from_spec(self):
        test_active_context = get_active_context()

        new_definition = create_schema_definition("schema")
        unused_definition = create_schema_definition("unused")
        actual_result = validate_unique_names(new_definition, unused_definition, test_active_context)

        assert_validator_result_failure(actual_result)


TEST_CONTENT = """
schema:
  name: Test0
  fields:
    - name: a
      type: string
---
schema:
  name: Test1
  fields:
    - name: b
      type: int
"""
