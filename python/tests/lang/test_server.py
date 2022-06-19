from unittest.async_case import IsolatedAsyncioTestCase

from tests.helpers.lsp.responses.hover_response import HoverResponse
from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.active_context = self.client.server.language_context

    async def test_adds_definitions_when_opening_file(self):
        await self.create_document("added.aac", TEST_DOCUMENT_ADDITIONAL_CONTENT)

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_content_changes(self):
        await self.create_document("test.aac", TEST_DOCUMENT_CONTENT)

        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        await self.write_document(f"{TEST_DOCUMENT_CONTENT}---{TEST_DOCUMENT_ADDITIONAL_CONTENT}")

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_hover_request(self):
        await self.create_document("test.aac", TEST_DOCUMENT_CONTENT)

        res: HoverResponse = await self.hover(self.document.file_name)

        self.assertIn("LSP server", res.get_content())


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
