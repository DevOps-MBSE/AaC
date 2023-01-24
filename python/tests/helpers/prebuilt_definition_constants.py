"""Module for providing a consistent set of re-usable definitions for testing."""
# The following flake linting is to ignore some hits on the commented example
#   structure for the test definitions
# flake8: noqa E800
import copy
from datetime import datetime

from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.plugins.validators import required_fields
from aac.plugins.validators import defined_references
from aac.lang.constants import (
    DEFINITION_FIELD_TYPE,
    DEFINITION_NAME_ROOT,
    PRIMITIVE_TYPE_BOOL,
    PRIMITIVE_TYPE_DATE,
    PRIMITIVE_TYPE_FILE,
    PRIMITIVE_TYPE_NUMBER,
    PRIMITIVE_TYPE_REFERENCE,
    PRIMITIVE_TYPE_STRING,
    PRIMITIVE_TYPE_INT,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_ARGUMENTS,
)

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_field_entry,
    create_schema_ext_definition,
    create_validation_entry,
    create_definition,
)

REFERENCE_CONTEXT = get_initialized_language_context()

# Validation Entries
DEFINED_REFERENCE_VALIDATION_NAME = defined_references.PLUGIN_NAME
DEFINED_REFERENCE_VALIDATION = create_validation_entry(DEFINED_REFERENCE_VALIDATION_NAME)

REQUIRED_FIELDS_VALIDATION_NAME = required_fields.PLUGIN_NAME
REQUIRED_FIELDS_VALIDATION = create_validation_entry(REQUIRED_FIELDS_VALIDATION_NAME)

# Inheritance Test Definitions
TEST_SCHEMA_PARENT_1_NAME = "Parent1"
TEST_SCHEMA_PARENT_1_FIELD_NAME = "P1F1"
TEST_SCHEMA_PARENT_1_FIELD_TYPE = PRIMITIVE_TYPE_INT
TEST_SCHEMA_PARENT_1_FIELD = create_field_entry(TEST_SCHEMA_PARENT_1_FIELD_NAME, TEST_SCHEMA_PARENT_1_FIELD_TYPE)
TEST_SCHEMA_PARENT_1_VALIDATION = copy.deepcopy(REQUIRED_FIELDS_VALIDATION)
TEST_SCHEMA_PARENT_1_VALIDATION_NAME = TEST_SCHEMA_PARENT_1_VALIDATION.get(DEFINITION_FIELD_NAME)
TEST_SCHEMA_PARENT_1_VALIDATION[DEFINITION_FIELD_ARGUMENTS] = [TEST_SCHEMA_PARENT_1_FIELD_NAME]
TEST_SCHEMA_PARENT_1 = create_schema_definition(
    TEST_SCHEMA_PARENT_1_NAME, fields=[TEST_SCHEMA_PARENT_1_FIELD], validations=[TEST_SCHEMA_PARENT_1_VALIDATION]
)

TEST_SCHEMA_PARENT_2_NAME = "Parent2"
TEST_SCHEMA_PARENT_2_FIELD_NAME = "P2F1"
TEST_SCHEMA_PARENT_2_FIELD_TYPE = PRIMITIVE_TYPE_STRING
TEST_SCHEMA_PARENT_2_FIELD = create_field_entry(TEST_SCHEMA_PARENT_2_FIELD_NAME, TEST_SCHEMA_PARENT_2_FIELD_TYPE)
TEST_SCHEMA_PARENT_2_VALIDATION = copy.deepcopy(DEFINED_REFERENCE_VALIDATION)
TEST_SCHEMA_PARENT_2_VALIDATION_NAME = TEST_SCHEMA_PARENT_2_VALIDATION.get(DEFINITION_FIELD_NAME)
TEST_SCHEMA_PARENT_2_VALIDATION[DEFINITION_FIELD_ARGUMENTS] = [TEST_SCHEMA_PARENT_2_FIELD_NAME]
TEST_SCHEMA_PARENT_2 = create_schema_definition(
    TEST_SCHEMA_PARENT_2_NAME, fields=[TEST_SCHEMA_PARENT_2_FIELD], validations=[TEST_SCHEMA_PARENT_2_VALIDATION]
)

TEST_SCHEMA_CHILD_NAME = "Child"
TEST_SCHEMA_CHILD_FIELD_NAME = "ChildField1"
TEST_SCHEMA_CHILD_FIELD_TYPE = PRIMITIVE_TYPE_STRING
TEST_SCHEMA_CHILD_FIELD = create_field_entry(TEST_SCHEMA_CHILD_FIELD_NAME, TEST_SCHEMA_CHILD_FIELD_TYPE)
TEST_SCHEMA_CHILD = create_schema_definition(
    TEST_SCHEMA_CHILD_NAME, fields=[TEST_SCHEMA_CHILD_FIELD], inherits=[TEST_SCHEMA_PARENT_1_NAME, TEST_SCHEMA_PARENT_2_NAME]
)

# Primitive Validation Definitions
SCHEMA_FIELD_INT = create_field_entry("intField", PRIMITIVE_TYPE_INT)
SCHEMA_FIELD_STRING = create_field_entry("stringField", PRIMITIVE_TYPE_STRING)
SCHEMA_FIELD_NUMBER = create_field_entry("numberField", PRIMITIVE_TYPE_NUMBER)
SCHEMA_FIELD_BOOL = create_field_entry("boolField", PRIMITIVE_TYPE_BOOL)
SCHEMA_FIELD_DATE = create_field_entry("dateField", PRIMITIVE_TYPE_DATE)
SCHEMA_FIELD_FILE = create_field_entry("fileField", PRIMITIVE_TYPE_FILE)
SCHEMA_FIELD_REFERENCE = create_field_entry("referenceField", PRIMITIVE_TYPE_REFERENCE)

TEST_TYPES_SCHEMA_DEFINITION = create_schema_definition(
    "TestPrimitiveTypeSchema",
    fields=[
        SCHEMA_FIELD_INT,
        SCHEMA_FIELD_STRING,
        SCHEMA_FIELD_NUMBER,
        SCHEMA_FIELD_BOOL,
        SCHEMA_FIELD_DATE,
        SCHEMA_FIELD_FILE,
        SCHEMA_FIELD_REFERENCE,
    ],
)

TEST_TYPES_ROOT_KEY = "primitive_tests"
TEST_TYPES_SCHEMA_EXTENSION_FIELD = create_field_entry(TEST_TYPES_ROOT_KEY, TEST_TYPES_SCHEMA_DEFINITION.name)
TEST_TYPES_SCHEMA_EXTENSION_DEFINITION = create_schema_ext_definition(
    f"{TEST_TYPES_SCHEMA_DEFINITION.name}Extension", DEFINITION_NAME_ROOT, fields=[TEST_TYPES_SCHEMA_EXTENSION_FIELD]
)
TEST_TYPES_VALID_INSTANCE = create_definition(
    TEST_TYPES_ROOT_KEY, "validPrimitives", {SCHEMA_FIELD_INT.get(DEFINITION_FIELD_NAME): 0}
)
TEST_TYPES_INVALID_INSTANCE = create_definition(
    TEST_TYPES_ROOT_KEY, "invalidPrimitives", {SCHEMA_FIELD_INT.get(DEFINITION_FIELD_NAME): 0.5}
)

# Definition with all core primitives

ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_NAME = "ALL_PRIMITIVES_TEST_DEFINITION"

all_primitives_fields = []
for field_type in REFERENCE_CONTEXT.get_primitive_types():
    all_primitives_fields.append(create_field_entry(field_type.upper(), field_type))

# "schema:
#  name: ALL_PRIMITIVES_TEST_DEFINITION
#  fields:
#  - name: DATE
#    type: date
#    description: ''
#  - name: DIRECTORY
#    type: directory
#    description: ''
#  - name: BOOL
#    type: bool
#    description: ''
#  - name: FILE
#    type: file
#    description: ''
#  - name: NUMBER
#    type: number
#    description: ''
#  - name: STRING
#    type: string
#    description: ''
#  - name: INT
#    type: int
#    description: ''
#  - name: REFERENCE
#    type: reference
#    description: ''
# "
ALL_PRIMITIVES_TEST_DEFINITION = create_schema_definition(
    ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_NAME, fields=all_primitives_fields
)

ALL_PRIMITIVES_ROOT_KEY = ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_NAME.lower()

# "ext:
#  name: ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT
#  type: root
#  description: ''
#  schemaExt:
#    add:
#    - name: all_primitives_test_definition
#      type: ALL_PRIMITIVES_TEST_DEFINITION
#      description: ''
#    required: []
# "
ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT_FIELD_NAME = "ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT_FIELD"
ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT_FIELD = create_field_entry(
    ALL_PRIMITIVES_ROOT_KEY, ALL_PRIMITIVES_TEST_DEFINITION.name
)
ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT_NAME = "ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT"
ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT = create_schema_ext_definition(
    ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT_NAME,
    DEFINITION_NAME_ROOT,
    fields=[ALL_PRIMITIVES_TEST_DEFINITION_SCHEMA_EXT_FIELD],
)

# "all_primitives_test_definition:
#  name: ALL_PRIMITIVES_INSTANCE
#  fields:
#  - name: string
#    type: testString
#    description: ''
#  - name: int
#    type: 10
#    description: ''
#  - name: bool
#    type: true
#    description: ''
#  - name: date
#    type: 2023-01-24 08:08:25.651387
#    description: ''
#  - name: number
#    type: 20.2
#    description: ''
# "

ALL_PRIMITIVES_INSTANCE_NAME = "ALL_PRIMITIVES_INSTANCE"
ALL_PRIMITIVES_INSTANCE_STRING_FIELD = create_field_entry(PRIMITIVE_TYPE_STRING.upper(), "testString")
ALL_PRIMITIVES_INSTANCE_INTEGER_FIELD = create_field_entry(PRIMITIVE_TYPE_INT.upper(), 10)
ALL_PRIMITIVES_INSTANCE_BOOL_FIELD = create_field_entry(PRIMITIVE_TYPE_BOOL.upper(), True)
ALL_PRIMITIVES_INSTANCE_DATE_FIELD = create_field_entry(PRIMITIVE_TYPE_DATE.upper(), datetime.now())
ALL_PRIMITIVES_INSTANCE_NUMBER_FIELD = create_field_entry(PRIMITIVE_TYPE_NUMBER.upper(), 20.2)
all_primitives_instance_fields = {
    field.get(DEFINITION_FIELD_NAME): field.get(DEFINITION_FIELD_TYPE)
    for field in [
        ALL_PRIMITIVES_INSTANCE_STRING_FIELD,
        ALL_PRIMITIVES_INSTANCE_INTEGER_FIELD,
        ALL_PRIMITIVES_INSTANCE_BOOL_FIELD,
        ALL_PRIMITIVES_INSTANCE_DATE_FIELD,
        ALL_PRIMITIVES_INSTANCE_NUMBER_FIELD,
    ]
}
ALL_PRIMITIVES_INSTANCE = create_definition(
    ALL_PRIMITIVES_ROOT_KEY, ALL_PRIMITIVES_INSTANCE_NAME, all_primitives_instance_fields
)
