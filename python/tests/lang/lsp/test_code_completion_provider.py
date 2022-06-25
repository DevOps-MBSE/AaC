from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types.language_features.completion import CompletionContext, CompletionParams, CompletionTriggerKind

from aac.lang.lsp.providers.code_completion_provider import SPACE_TRIGGER

from tests.helpers.lsp.responses.completion_response import CompletionResponse
from tests.lang.lsp.base_lsp_test_case import BaseLspTestCase, TEST_DOCUMENT_NAME, TEST_PARTIAL_CONTENT


class TestCodeCompletionProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
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
                **self.build_text_document_position_params(file_name, line, character)
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
