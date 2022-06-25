from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types.basic_structures import Position, TextDocumentIdentifier
from pygls.lsp.types.language_features.completion import CompletionContext, CompletionParams, CompletionTriggerKind

from aac.lang.lsp.providers.code_completion_provider import SPACE_TRIGGER

from tests.helpers.lsp.responses.completion_response import CompletionResponse
from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestCodeCompletionProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.active_context = self.client.server.language_context
        await self.create_document(TEST_DOCUMENT_NAME, TEST_DOCUMENT_CONTENT)

    async def complete(self, file_name: str, line: int = 0, character: int = 0, trigger_kind: CompletionTriggerKind = CompletionTriggerKind.TriggerCharacter, trigger_character: str = SPACE_TRIGGER) -> CompletionResponse:
        """
        Send a code completion request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the code completion action.
            line (int): The line number (starting from 0) at which to perform the code completion action.
            character (int): The character number (starting from 0) at which to perform the code completion action.
            trigger_kind (CompletionTriggerKind): The action that triggered the code completion action.
            trigger_caracter (str): The character that triggered/triggers the code completion action.

        Returns:
            A CompletionResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            CompletionResponse,
            methods.COMPLETION,
            CompletionParams(
                context=CompletionContext(trigger_kind=trigger_kind, trigger_character=trigger_character),
                text_document=TextDocumentIdentifier(uri=self.to_uri(file_name)),
                position=Position(line=line, character=character),
            ),
        )

    async def test_handles_completion_request(self):
        new_content = f"{TEST_PARTIAL_CONTENT}{SPACE_TRIGGER}"
        await self.write_document(TEST_DOCUMENT_NAME, new_content)

        last_line_num = len(new_content.splitlines()) - 1
        last_char_num = len(new_content.splitlines()[last_line_num]) - 1
        res: CompletionResponse = await self.complete(TEST_DOCUMENT_NAME, line=last_line_num, character=last_char_num)

        self.assertGreater(len(res.get_completion_items()), 0)
        self.assertIsNotNone(res.get_completion_item_by_label("string"))


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
