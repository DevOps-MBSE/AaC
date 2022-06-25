from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types.basic_structures import Position, TextDocumentIdentifier
from pygls.lsp.types.language_features.definition import DefinitionParams

from aac.parser._parse_source import YAML_DOCUMENT_SEPARATOR

from tests.helpers.lsp.responses.goto_definition_response import GotoDefinitionResponse
from tests.lang.lsp.base_lsp_test_case import BaseLspTestCase


class TestGotoDefinitionProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.active_context = self.client.server.language_context
        await self.create_document(TEST_DOCUMENT_NAME, TEST_DOCUMENT_CONTENT)

    async def goto_definition(self, file_name: str, line: int = 0, character: int = 0) -> GotoDefinitionResponse:
        """
        Send a goto definition request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the goto definition action.
            line (int): The line number (starting from 0) at which to perform the goto definition action.
            character (int): The character number (starting from 0) at which to perform the goto definition action.

        Returns:
            A GotoDefinitionResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            GotoDefinitionResponse,
            methods.DEFINITION,
            DefinitionParams(
                text_document=TextDocumentIdentifier(uri=self.to_uri(file_name)),
                position=Position(line=line, character=character),
            )
        )

    async def test_get_ranges_containing_name(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)
        text_range, *rest = goto_definition_provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_DOCUMENT_SCHEMA_NAME)
        self.assertEqual(len(rest) + 1, TEST_DOCUMENT_CONTENT.count(TEST_DOCUMENT_SCHEMA_NAME))

        self.assertEqual(text_range.start, Position(line=2, character=8))
        self.assertEqual(text_range.end, Position(line=2, character=8 + len(TEST_DOCUMENT_SCHEMA_NAME)))

    async def test_get_named_location(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)
        document_uri = self.to_uri(TEST_DOCUMENT_NAME)
        location, *_ = goto_definition_provider.get_definition_location(
            {document_uri: self.virtual_document_to_lsp_document(TEST_DOCUMENT_NAME)},
            document_uri,
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

    async def test_handles_goto_definition_request_when_definition_in_different_document(self):
        goto_definition_provider = self.client.server.providers.get(methods.DEFINITION)

        added_content = f"{TEST_PARTIAL_CONTENT} {TEST_ADDITIONAL_SCHEMA_NAME}"
        added_document = await self.create_document("added.aac", added_content)

        new_test_document_content = f"{TEST_DOCUMENT_CONTENT}{YAML_DOCUMENT_SEPARATOR}{TEST_ADDITIONAL_MODEL_CONTENT}"
        await self.write_document(TEST_DOCUMENT_NAME, new_test_document_content)

        text_range, *_ = goto_definition_provider.get_ranges_containing_name(new_test_document_content, TEST_ADDITIONAL_SCHEMA_NAME)
        line = text_range.start.line
        character = text_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        definition_range, *_ = goto_definition_provider.get_ranges_containing_name(added_content, TEST_ADDITIONAL_SCHEMA_NAME)

        location = res.get_location()
        self.assertEqual(location.uri, self.to_uri(added_document.file_name))
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
