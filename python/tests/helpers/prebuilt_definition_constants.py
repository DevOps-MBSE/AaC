"""Module for providing a consistent set of re-usable definitions for testing."""
import copy
from aac.plugins.validators import required_fields
from aac.plugins.validators import defined_references

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_field_entry,
    create_validation_entry,
)


# Validation Entries
DEFINED_REFERENCE_VALIDATION_NAME = defined_references.PLUGIN_NAME
DEFINED_REFERENCE_VALIDATION = create_validation_entry(DEFINED_REFERENCE_VALIDATION_NAME)

REQUIRED_FIELDS_VALIDATION_NAME = required_fields.PLUGIN_NAME
REQUIRED_FIELDS_VALIDATION = create_validation_entry(REQUIRED_FIELDS_VALIDATION_NAME)

# Inheritance Test Definitions
TEST_SCHEMA_PARENT_1_NAME = "Parent1"
TEST_SCHEMA_PARENT_1_FIELD_NAME = "P1F1"
TEST_SCHEMA_PARENT_1_FIELD_TYPE = "integer"
TEST_SCHEMA_PARENT_1_FIELD = create_field_entry(TEST_SCHEMA_PARENT_1_FIELD_NAME, TEST_SCHEMA_PARENT_1_FIELD_TYPE)
TEST_SCHEMA_PARENT_1_VALIDATION = copy.deepcopy(REQUIRED_FIELDS_VALIDATION)
TEST_SCHEMA_PARENT_1_VALIDATION_NAME = TEST_SCHEMA_PARENT_1_VALIDATION.get("name")
TEST_SCHEMA_PARENT_1_VALIDATION["arguments"] = [TEST_SCHEMA_PARENT_1_FIELD_NAME]
TEST_SCHEMA_PARENT_1 = create_schema_definition(TEST_SCHEMA_PARENT_1_NAME, fields=[TEST_SCHEMA_PARENT_1_FIELD], validations=[TEST_SCHEMA_PARENT_1_VALIDATION])

TEST_SCHEMA_PARENT_2_NAME = "Parent2"
TEST_SCHEMA_PARENT_2_FIELD_NAME = "P2F1"
TEST_SCHEMA_PARENT_2_FIELD_TYPE = "string"
TEST_SCHEMA_PARENT_2_FIELD = create_field_entry(TEST_SCHEMA_PARENT_2_FIELD_NAME, TEST_SCHEMA_PARENT_2_FIELD_TYPE)
TEST_SCHEMA_PARENT_2_VALIDATION = copy.deepcopy(DEFINED_REFERENCE_VALIDATION)
TEST_SCHEMA_PARENT_2_VALIDATION_NAME = TEST_SCHEMA_PARENT_2_VALIDATION.get("name")
TEST_SCHEMA_PARENT_2_VALIDATION["arguments"] = [TEST_SCHEMA_PARENT_2_FIELD_NAME]
TEST_SCHEMA_PARENT_2 = create_schema_definition(TEST_SCHEMA_PARENT_2_NAME, fields=[TEST_SCHEMA_PARENT_2_FIELD], validations=[TEST_SCHEMA_PARENT_2_VALIDATION])

TEST_SCHEMA_CHILD_NAME = "Child"
TEST_SCHEMA_CHILD_FIELD_NAME = "ChildField1"
TEST_SCHEMA_CHILD_FIELD_TYPE = "string"
TEST_SCHEMA_CHILD_FIELD = create_field_entry(TEST_SCHEMA_CHILD_FIELD_NAME, TEST_SCHEMA_CHILD_FIELD_TYPE)
TEST_SCHEMA_CHILD = create_schema_definition(TEST_SCHEMA_CHILD_NAME, fields=[TEST_SCHEMA_CHILD_FIELD], inherits=[TEST_SCHEMA_PARENT_1_NAME, TEST_SCHEMA_PARENT_2_NAME])