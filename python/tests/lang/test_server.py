from aac.lang.active_context_lifecycle_manager import get_active_context

from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = self.create_document("test.aac", TEST_DOCUMENT_CONTENT)

    def test_adds_definitions_when_opening_file(self):
        self.create_document("added.aac", TEST_DOCUMENT_ADDITIONAL_CONTENT)

        active_context = get_active_context()
        self.assertIsNotNone(active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    def test_handles_content_changes(self):
        new_content = f"{TEST_DOCUMENT_CONTENT}---{TEST_DOCUMENT_ADDITIONAL_CONTENT}"

        active_context = get_active_context()
        self.assertIsNone(active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        self.write_document(new_content)

        self.assertIsNotNone(active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    def test_handles_hover_request(self):
        res = self.hover(self.document.file_name)

        self.assertSequenceEqual(list(res.keys()), ["contents"])
        self.assertIn("LSP server", res.get("contents"))


TEST_ADDITIONAL_SCHEMA_NAME = "DataC"
TEST_ADDITIONAL_MODEL_NAME = "ServiceTwo"
TEST_DOCUMENT_CONTENT = """
schema:
  name: DataA
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
  name: ServiceOne
  behavior:
    - name: Process DataA Request
      type: request-response
      description: Process a DataA request and return a DataB response
      input:
        - name: in
          type: DataA
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
