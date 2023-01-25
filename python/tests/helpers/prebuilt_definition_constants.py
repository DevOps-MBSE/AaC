"""Module for providing a consistent set of re-usable definitions for testing."""
import copy

from aac.io.constants import DEFINITION_SEPARATOR
from aac.plugins.validators import required_fields
from aac.plugins.validators import defined_references
from aac.lang.constants import (
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
    create_behavior_entry,
    create_definition,
    create_enum_definition,
    create_field_entry,
    create_model_definition,
    create_scenario_entry,
    create_schema_definition,
    create_schema_ext_definition,
    create_validation_entry,
)


# Standard Test Schemas
TEST_SCHEMA_A = create_schema_definition("DataA", fields=[create_field_entry("msg", "string")])
TEST_SCHEMA_B = create_schema_definition("DataB", fields=[create_field_entry("msg", "string")])
TEST_SCHEMA_C = create_schema_definition("DataC", fields=[create_field_entry("msg", "string")])

# Standard Test Enums
TEST_ENUM = create_enum_definition("Options", ["one", "two", "three"])

# Standard Test Models
TEST_SERVICE_ONE_NAME = "ServiceOne"
TEST_SERVICE_ONE_BEHAVIOR = create_behavior_entry(
    f"Process {TEST_SCHEMA_A.name} Request",
    "request-response",
    f"Process a {TEST_SCHEMA_A.name} request and return a {TEST_SCHEMA_B.name} response",
    input=[create_field_entry("in", TEST_SCHEMA_A.name)],
    output=[create_field_entry("out", TEST_SCHEMA_B.name)],
    acceptance=[
        create_scenario_entry(
            f"Receive {TEST_SCHEMA_A.name} request and return {TEST_SCHEMA_B.name} response",
            given=[f"{TEST_SERVICE_ONE_NAME} is running"],
            when=[f"{TEST_SERVICE_ONE_NAME} receives a {TEST_SCHEMA_A.name} request"],
            then=[
                f"{TEST_SERVICE_ONE_NAME} processes the request into a {TEST_SCHEMA_B.name} response",
                f"{TEST_SERVICE_ONE_NAME} returns the {TEST_SCHEMA_B.name} response",
            ],
        ),
        create_scenario_entry(
            "Receive invalid request",
            given=[f"{TEST_SERVICE_ONE_NAME} is running"],
            when=[f"{TEST_SERVICE_ONE_NAME} receives request that isn't a {TEST_SCHEMA_A.name} request"],
            then=[f"{TEST_SERVICE_ONE_NAME} returns an error response code"],
        ),
    ],
)
TEST_SERVICE_ONE = create_model_definition(TEST_SERVICE_ONE_NAME, behavior=[TEST_SERVICE_ONE_BEHAVIOR])

TEST_SERVICE_TWO_NAME = "ServiceTwo"
TEST_SERVICE_TWO_BEHAVIOR = create_behavior_entry(
    f"Process {TEST_SCHEMA_B.name} Request",
    "request-response",
    f"Process a {TEST_SCHEMA_B.name} request and return a DataC response",
    input=[create_field_entry("in", TEST_SCHEMA_B.name)],
    output=[create_field_entry("out", TEST_SCHEMA_C.name)],
    acceptance=[
        create_scenario_entry(
            f"Receive {TEST_SCHEMA_B.name} request and return {TEST_SCHEMA_C.name} response",
            given=[f"{TEST_SERVICE_TWO_NAME} is running"],
            when=[f"{TEST_SERVICE_TWO_NAME} receives a {TEST_SCHEMA_B.name} request"],
            then=[
                f"{TEST_SERVICE_TWO_NAME} processes the request into a DataC response",
                f"{TEST_SERVICE_TWO_NAME} returns the DataC response",
            ],
        )
    ],
)
TEST_SERVICE_TWO = create_model_definition(TEST_SERVICE_TWO_NAME, behavior=[TEST_SERVICE_TWO_BEHAVIOR])

TEST_SERVICE_THREE_NAME = "ServiceThree"
TEST_SERVICE_THREE_BEHAVIOR = create_behavior_entry(
    "Pass through",
    "request-response",
    f"Process a {TEST_SCHEMA_C.name} request and return a {TEST_SCHEMA_C.name} response",
    input=[create_field_entry("in", TEST_SCHEMA_C.name)],
    output=[create_field_entry("out", TEST_SCHEMA_C.name)],
    acceptance=[
        create_scenario_entry(
            "Pass the data through, untouched",
            when=[f"{TEST_SERVICE_THREE_NAME} receives a {TEST_SCHEMA_C.name} request"],
            then=[f"{TEST_SERVICE_THREE_NAME} returns the {TEST_SCHEMA_C.name} data in the response, untouched"],
        )
    ],
)
TEST_SERVICE_THREE = create_model_definition(TEST_SERVICE_THREE_NAME, behavior=[TEST_SERVICE_THREE_BEHAVIOR])


# Test File/Document data
TEST_DOCUMENT_NAME = "test.aac"
TEST_DOCUMENT_CONTENT = DEFINITION_SEPARATOR.join([TEST_SCHEMA_A.to_yaml(), TEST_SCHEMA_B.to_yaml(), TEST_SERVICE_ONE.to_yaml()])


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
        SCHEMA_FIELD_REFERENCE
    ]
)

TEST_TYPES_ROOT_KEY = "primitive_tests"
TEST_TYPES_SCHEMA_EXTENSION_FIELD = create_field_entry(TEST_TYPES_ROOT_KEY, TEST_TYPES_SCHEMA_DEFINITION.name)
TEST_TYPES_SCHEMA_EXTENSION_DEFINITION = create_schema_ext_definition(f"{TEST_TYPES_SCHEMA_DEFINITION.name}Extension", DEFINITION_NAME_ROOT, fields=[TEST_TYPES_SCHEMA_EXTENSION_FIELD])
TEST_TYPES_VALID_INSTANCE = create_definition(TEST_TYPES_ROOT_KEY, "validPrimitives", {SCHEMA_FIELD_INT.get("name"): 0})
TEST_TYPES_INVALID_INSTANCE = create_definition(TEST_TYPES_ROOT_KEY, "invalidPrimitives", {SCHEMA_FIELD_INT.get("name"): 0.5})


# LSP Test Definitions
TEST_ROOT_SCHEMA = create_schema_definition("NewRootKeyStructure", fields=[create_field_entry("name", "string"), create_field_entry("test_enum", TEST_ENUM.name)])
TEST_ROOT_EXTENSION = create_schema_ext_definition("TestRootExtension", DEFINITION_NAME_ROOT, fields=[create_field_entry("test_root", TEST_ROOT_SCHEMA.name)])
TEST_ROOT_INSTANCE = create_definition("test_root", "TestRootInstance", {"test_enum": "one"})

TEST_DOCUMENT_WITH_ENUM_NAME = f"enum_{TEST_DOCUMENT_NAME}"
TEST_DOCUMENT_WITH_ENUM_CONTENT = DEFINITION_SEPARATOR.join(
    [
        TEST_ROOT_SCHEMA.to_yaml(),
        TEST_ROOT_EXTENSION.to_yaml(),
        TEST_ENUM.to_yaml(),
        TEST_ROOT_INSTANCE.to_yaml(),
    ]
)

TEST_PARTIAL_CONTENT_NAME = "Partial"
TEST_PARTIAL_CONTENT = f"""
schema:
  name: {TEST_PARTIAL_CONTENT_NAME}
  fields:
  - name: msg
    type:\
"""

MALFORMED_EXTRA_FIELD_NAME = "extrafield"
MALFORMED_EXTRA_FIELD_CONTENT = "extracontent"
TEST_MALFORMED_CONTENT = f"""
model:
  name: {TEST_SERVICE_TWO_NAME}
  {MALFORMED_EXTRA_FIELD_NAME}: {MALFORMED_EXTRA_FIELD_CONTENT}
  behavior:
    - name: Process {TEST_SCHEMA_B.name} Request
      type: request-response
      description: Process a {TEST_SCHEMA_B.name} request and return a {TEST_SCHEMA_C.name} response
      input:
        - name: in
          type: {TEST_SCHEMA_B.name}
      output:
        - name: out
          type: {TEST_SCHEMA_C.name}
          {MALFORMED_EXTRA_FIELD_NAME}: {MALFORMED_EXTRA_FIELD_CONTENT}
      acceptance:
        - scenario: Receive {TEST_SCHEMA_B.name} request and return {TEST_SCHEMA_C.name} response
          given:
            - {TEST_SERVICE_TWO_NAME} is running
          when:
            - {TEST_SERVICE_TWO_NAME} receives a {TEST_SCHEMA_B.name} request
          then:
            - {TEST_SERVICE_TWO_NAME} processes the request into a {TEST_SCHEMA_C.name} response
            - {TEST_SERVICE_TWO_NAME} returns the {TEST_SCHEMA_C.name} response
          {MALFORMED_EXTRA_FIELD_NAME}: {MALFORMED_EXTRA_FIELD_CONTENT}
"""
