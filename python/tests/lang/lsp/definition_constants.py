TEST_DOCUMENT_NAME = "test.aac"
TEST_DOCUMENT_MODEL_NAME = "ServiceOne"
TEST_DOCUMENT_SCHEMA_NAME = "DataA"
TEST_ADDITIONAL_SCHEMA_NAME = "DataC"
TEST_ADDITIONAL_MODEL_NAME = "ServiceTwo"
TEST_ENUM_NAME = "Options"

TEST_DOCUMENT_CONTENT = f"""
schema:
  name: {TEST_DOCUMENT_SCHEMA_NAME}
  fields:
  - name: msg
    type: string
---
schema:
  name: DataB
  fields:
  - name: msg
    type: string
---
model:
  name: {TEST_DOCUMENT_MODEL_NAME}
  behavior:
    - name: Process DataA Request
      type: request-response
      description: Process a DataA request and return a DataB response
      input:
        - name: in
          type: {TEST_DOCUMENT_SCHEMA_NAME}
      output:
        - name: out
          type: DataB
      acceptance:
        - scenario: Receive DataA request and return DataB response
          given:
            - ServiceOne is running
          when:
            - ServiceOne receives a DataA request
          then:
            - ServiceOne processes the request into a DataB response
            - ServiceOne returns the DataB response
        - scenario: Receive invalid request
          given:
            - ServiceOne is running
          when:
            - ServiceOne receives request that isn't a DataA request
          then:
            - ServiceOne returns an error response code
"""
TEST_DOCUMENT_ADDITIONAL_CONTENT = f"""
schema:
  name: {TEST_ADDITIONAL_SCHEMA_NAME}
  fields:
  - name: msg
    type: string
---
model:
  name: {TEST_ADDITIONAL_MODEL_NAME}
  behavior:
    - name: Process DataB Request
      type: request-response
      description: Process a DataB request and return a DataC response
      input:
        - name: in
          type: DataB
      output:
        - name: out
          type: DataC
      acceptance:
        - scenario: Receive DataB request and return DataC response
          given:
            - ServiceTwo is running
          when:
            - ServiceTwo receives a DataB request
          then:
            - ServiceTwo processes the request into a DataC response
            - ServiceTwo returns the DataC response
"""
TEST_PARTIAL_CONTENT = f"""
schema:
  name: {TEST_ADDITIONAL_SCHEMA_NAME}
  fields:
  - name: msg
    type:\
"""
TEST_ADDITIONAL_MODEL_CONTENT = f"""
model:
  name: ServiceThree
  behavior:
    - name: Pass through
      type: request-response
      input:
        - name: in
          type: {TEST_ADDITIONAL_SCHEMA_NAME}
      output:
        - name: out
          type: {TEST_ADDITIONAL_SCHEMA_NAME}
      acceptance:
        - scenario: Pass the data through, untouched
          when:
            - ServiceThree receives a {TEST_ADDITIONAL_SCHEMA_NAME} request
          then:
            - ServiceThree returns the {TEST_ADDITIONAL_SCHEMA_NAME} data in the response, untouched
"""
TEST_ENUM_CONTENT = f"""
enum:
  name: {TEST_ENUM_NAME}
  values:
    - one
    - two
    - three
"""
