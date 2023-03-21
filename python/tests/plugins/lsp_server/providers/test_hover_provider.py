from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types import HoverParams

from tests.helpers.lsp.responses.hover_response import HoverResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_CONTENT,
    TEST_DOCUMENT_NAME,
    TEST_SCHEMA_A
)


class TestHoverProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def hover(self, file_name: str, line: int = 0, character: int = 0) -> HoverResponse:
        """
        Send a hover request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the hover action.
            line (int): The line number (starting from 0) at which to perform the hover action.
            character (int): The character number (starting from 0) at which to perform the hover action.

        Returns:
            A HoverResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            HoverResponse,
            methods.HOVER,
            HoverParams(**self.build_text_document_position_params(file_name, line, character)),
        )

    async def test_handles_hover_request(self):
        res: HoverResponse = await self.hover(TEST_DOCUMENT_NAME, 1, 8)
        self.assertEqual(res.get_content(), self.active_context.get_definition_by_name(TEST_SCHEMA_A.name).content)

    async def test_no_hover_when_nothing_under_cursor(self):
        await self.write_document(TEST_DOCUMENT_NAME, f"\n{TEST_DOCUMENT_CONTENT}")
        res: HoverResponse = await self.hover(TEST_DOCUMENT_NAME)
        self.assertIsNone(res.get_content())
