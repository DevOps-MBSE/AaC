from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types.basic_structures import Position

from aac.lang.lsp.providers.code_completion_provider import SPACE_TRIGGER

from tests.helpers.lsp.responses.hover_response import HoverResponse
from tests.helpers.lsp.responses.completion_response import CompletionResponse
from tests.helpers.lsp.responses.goto_definition_response import GotoDefinitionResponse
from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.active_context = self.client.server.language_context
        await self.create_document(TEST_DOCUMENT_NAME, TEST_DOCUMENT_CONTENT)

    async def test_adds_definitions_when_opening_file(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        await self.create_document("added.aac", TEST_DOCUMENT_ADDITIONAL_CONTENT)

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_content_changes(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        await self.write_document(TEST_DOCUMENT_NAME, f"{TEST_DOCUMENT_CONTENT}---{TEST_DOCUMENT_ADDITIONAL_CONTENT}")

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_hover_request(self):
        res: HoverResponse = await self.hover(TEST_DOCUMENT_NAME)
        self.assertIn("LSP server", res.get_content())

    async def test_handles_completion_request(self):
        new_content = f"{TEST_PARTIAL_CONTENT}{SPACE_TRIGGER}"
        await self.write_document(TEST_DOCUMENT_NAME, new_content)

        last_line_num = len(new_content.splitlines()) - 1
        last_char_num = len(new_content.splitlines()[last_line_num]) - 1
        res: CompletionResponse = await self.complete(TEST_DOCUMENT_NAME, line=last_line_num, character=last_char_num)

        self.assertGreater(len(res.get_completion_items()), 0)
        self.assertIsNotNone(res.get_completion_item_by_label("string"))

    async def test_get_cursor_position(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)
        text_range, *rest = goto_definition_provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_DOCUMENT_SCHEMA_NAME)
        self.assertEqual(len(rest) + 1, TEST_DOCUMENT_CONTENT.count(TEST_DOCUMENT_SCHEMA_NAME))

        self.assertEqual(text_range.start, Position(line=2, character=8))
        self.assertEqual(text_range.end, Position(line=2, character=8 + len(TEST_DOCUMENT_SCHEMA_NAME)))

    async def test_get_named_location(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)
        location, *_ = goto_definition_provider.get_definition_location(
            self.virtual_document_to_lsp_document(TEST_DOCUMENT_NAME),
            Position(line=21, character=17),
        )

        self.assertEqual(location.range.start, Position(line=2, character=8))
        self.assertEqual(location.range.end, Position(line=2, character=8 + len(TEST_DOCUMENT_SCHEMA_NAME)))

    async def test_handles_goto_definition_request_when_cursor_at_definition(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)
        text_range, *_ = goto_definition_provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_DOCUMENT_SCHEMA_NAME)
        line = text_range.start.line
        character = text_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        location = res.get_location()
        self.assertEqual(location.range.start, Position(line=line, character=character))
        self.assertEqual(location.range.end, Position(line=line, character=character + len(TEST_DOCUMENT_SCHEMA_NAME)))

    async def test_handles_goto_definition_request_when_definition_in_same_document(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)
        definition_range, text_range, *_ = goto_definition_provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_DOCUMENT_SCHEMA_NAME)
        line = text_range.start.line
        character = text_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        location = res.get_location()
        self.assertEqual(location.range.start, Position(line=definition_range.start.line, character=definition_range.start.character))
        self.assertEqual(location.range.end, Position(line=definition_range.end.line, character=definition_range.end.character))


TEST_DOCUMENT_NAME = "test.aac"
TEST_DOCUMENT_MODEL_NAME = "ServiceOne"
TEST_DOCUMENT_SCHEMA_NAME = "DataA"
TEST_ADDITIONAL_SCHEMA_NAME = "DataC"
TEST_ADDITIONAL_MODEL_NAME = "ServiceTwo"
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
