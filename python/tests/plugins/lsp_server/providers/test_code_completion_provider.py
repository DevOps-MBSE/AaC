from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types import CompletionContext, CompletionParams, CompletionTriggerKind
from aac.lang.definitions.search import search_definition

from aac.plugins.first_party.lsp_server.providers.code_completion_provider import SPACE_TRIGGER

from tests.helpers.lsp.responses.completion_response import CompletionResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import TEST_DOCUMENT_NAME, TEST_PARTIAL_CONTENT


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

    def get_all_defined_type_names(self) -> list[str]:
        """Return a list of all defined type names."""
        schemas = self.active_context.get_definitions_by_root_key("schema")
        enums = self.active_context.get_definitions_by_root_key("enum")

        all_defined_type_names = [definition.name for definition in schemas]
        [all_defined_type_names.extend(search_definition(enum, ["enum", "values"])) for enum in enums]

        return all_defined_type_names

    async def test_handles_completion_request(self):
        new_content = f"{TEST_PARTIAL_CONTENT}{SPACE_TRIGGER}"
        await self.write_document(TEST_DOCUMENT_NAME, new_content)

        last_line = len(new_content.splitlines()) - 1
        last_char = len(new_content.splitlines()[last_line]) - 1
        res: CompletionResponse = await self.complete(TEST_DOCUMENT_NAME, line=last_line, character=last_char)

        self.assertGreater(len(res.get_completion_items()), 0)
        [self.assertIn(name, self.get_all_defined_type_names()) for name in res.get_completion_item_names()]
