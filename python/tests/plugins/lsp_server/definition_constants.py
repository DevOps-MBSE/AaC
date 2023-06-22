from aac.io.constants import DEFINITION_SEPARATOR
from aac.lang.constants import BEHAVIOR_TYPE_REQUEST_RESPONSE, DEFINITION_NAME_ROOT

from tests.helpers.parsed_definitions import (
    create_enum_definition,
    create_schema_definition,
    create_field_entry,
    create_model_definition,
    create_behavior_entry,
    create_scenario_entry,
    create_schema_ext_definition,
    create_definition,
)

TEST_ENUM = create_enum_definition("Options", ["one", "two", "three"])
TEST_SCHEMA_A = create_schema_definition(
    "Data A", fields=[create_field_entry("msg", "string")]
)  # Space in the name is specifically to test #390
TEST_SCHEMA_B = create_schema_definition("DataB", fields=[create_field_entry("msg", "string")])
TEST_SCHEMA_C = create_schema_definition("DataC", fields=[create_field_entry("msg", "string")])
TEST_ROOT_SCHEMA = create_schema_definition(
    "NewRootKeyStructure", fields=[create_field_entry("name", "string"), create_field_entry("test_enum", TEST_ENUM.name)]
)
TEST_ROOT_EXTENSION = create_schema_ext_definition(
    "TestRootExtension", DEFINITION_NAME_ROOT, fields=[create_field_entry("test_root", TEST_ROOT_SCHEMA.name)]
)
TEST_ROOT_INSTANCE = create_definition("test_root", "TestRootInstance", {"test_enum": "one"})

TEST_PARTIAL_CONTENT_NAME = "Partial"
TEST_PARTIAL_CONTENT = f"""
schema:
  name: {TEST_PARTIAL_CONTENT_NAME}
  fields:
  - name: msg
    type:\
"""

TEST_SERVICE_ONE_NAME = "ServiceOne"
TEST_SERVICE_ONE_BEHAVIOR = create_behavior_entry(
    f"Process {TEST_SCHEMA_A.name} Request",
    BEHAVIOR_TYPE_REQUEST_RESPONSE,
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
    BEHAVIOR_TYPE_REQUEST_RESPONSE,
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
    BEHAVIOR_TYPE_REQUEST_RESPONSE,
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

TEST_DOCUMENT_NAME = "test.aac"
TEST_DOCUMENT_WITH_ENUM_NAME = "enum_test.aac"
TEST_DOCUMENT_CONTENT = DEFINITION_SEPARATOR.join(
    [TEST_SCHEMA_A.to_yaml(), TEST_SCHEMA_B.to_yaml(), TEST_SERVICE_ONE.to_yaml()]
)
TEST_DOCUMENT_WITH_ENUM_CONTENT = DEFINITION_SEPARATOR.join(
    [
        TEST_ROOT_SCHEMA.to_yaml(),
        TEST_ROOT_EXTENSION.to_yaml(),
        TEST_ENUM.to_yaml(),
        TEST_ROOT_INSTANCE.to_yaml(),
    ]
)

MALFORMED_EXTRA_FIELD_NAME = "extrafield"
MALFORMED_EXTRA_FIELD_CONTENT = "extracontent"
TEST_MALFORMED_CONTENT = f"""
model:
  name: {TEST_SERVICE_TWO_NAME}
  {MALFORMED_EXTRA_FIELD_NAME}: {MALFORMED_EXTRA_FIELD_CONTENT}
  behavior:
    - name: Process {TEST_SCHEMA_B.name} Request
      type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
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
