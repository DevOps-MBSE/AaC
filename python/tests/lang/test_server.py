from unittest.async_case import IsolatedAsyncioTestCase

from aac.lang.lsp.code_completion_provider import SPACE_TRIGGER

from tests.helpers.lsp.responses.hover_response import HoverResponse
from tests.helpers.lsp.responses.completion_response import CompletionResponse
from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.active_context = self.client.server.language_context
        await self.create_document("test.aac", TEST_DOCUMENT_CONTENT)

    async def test_adds_definitions_when_opening_file(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))             
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))
        
        await self.create_document("added.aac", TEST_DOCUMENT_ADDITIONAL_CONTENT)

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_content_changes(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        await self.write_document(f"{TEST_DOCUMENT_CONTENT}---{TEST_DOCUMENT_ADDITIONAL_CONTENT}")

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_hover_request(self):
        res: HoverResponse = await self.hover()
        self.assertIn("LSP server", res.get_content())

    async def test_handles_completion_request(self):
        new_content = f"{TEST_PARTIAL_CONTENT}{SPACE_TRIGGER}"
        await self.write_document(new_content)

        last_line_num = len(new_content.splitlines()) - 1
        last_char_num = len(new_content.splitlines()[last_line_num]) - 1
        res: CompletionResponse = await self.complete(line=last_line_num, character=last_char_num)

        self.assertGreater(len(res.get_completion_items()), 0)
        self.assertIsNotNone(res.get_completion_item_by_label("string"))


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
TEST_PARTIAL_CONTENT = f"""
schema:
  name: {TEST_ADDITIONAL_SCHEMA_NAME}
  fields:
  - name: msg
    type:\
"""
