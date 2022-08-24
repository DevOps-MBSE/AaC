from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types.language_features.references import ReferenceParams

from tests.helpers.lsp.responses.find_references_response import FindReferencesResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_CONTENT,
    TEST_DOCUMENT_NAME,
)


class TestFindReferencesProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def hover(self, file_name: str, line: int = 0, character: int = 0) -> FindReferencesResponse:
        """
        Send a hover request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the hover action.
            line (int): The line number (starting from 0) at which to perform the hover action.
            character (int): The character number (starting from 0) at which to perform the hover action.

        Returns:
            A FindReferencesResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            FindReferencesResponse,
            methods.REFERENCES,
            ReferenceParams(**self.build_text_document_position_params(file_name, line, character)),
        )

    async def test_todo(self):
        pass
