from aac.io.constants import YAML_DOCUMENT_SEPARATOR

from tests.helpers.parsed_definitions import (
    create_enum_definition,
    create_schema_definition,
    create_field_entry,
    create_model_definition,
    create_behavior_entry,
    create_scenario_entry,
)

TEST_ENUM = create_enum_definition("Options", ["one", "two", "three"])
TEST_SCHEMA_A = create_schema_definition("DataA", fields=[create_field_entry("msg", "string")])
TEST_SCHEMA_B = create_schema_definition("DataB", fields=[create_field_entry("msg", "string")])
TEST_SCHEMA_C = create_schema_definition("DataC", fields=[create_field_entry("msg", "string")])

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
    ]
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
    ]
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
    ]
)
TEST_SERVICE_THREE = create_model_definition(TEST_SERVICE_THREE_NAME, behavior=[TEST_SERVICE_THREE_BEHAVIOR])

TEST_DOCUMENT_NAME = "test.aac"
TEST_DOCUMENT_CONTENT = f"{YAML_DOCUMENT_SEPARATOR}\n".join([TEST_SCHEMA_A.to_yaml(), TEST_SCHEMA_B.to_yaml(), TEST_ENUM.to_yaml(), TEST_SERVICE_ONE.to_yaml()])

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
