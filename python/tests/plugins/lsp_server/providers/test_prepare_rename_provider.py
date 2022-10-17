from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types import PrepareRenameParams, Range

from tests.helpers.lsp.responses.prepare_rename_response import PrepareRenameResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_CONTENT,
    TEST_DOCUMENT_NAME,
)


class TestPrepareRenameProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def prepare_rename(self, file_name: str, line: int = 0, character: int = 0) -> PrepareRenameResponse:
        """
        Send a prepare rename request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the prepare rename action.
            line (int): The line number (starting from 0) at which to perform the prepare rename action.
            character (int): The character number (starting from 0) at which to perform the prepare rename action.

        Returns:
            A PrepareRenameResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            PrepareRenameResponse,
            methods.PREPARE_RENAME,
            PrepareRenameParams(**self.build_text_document_position_params(file_name, line, character)),
        )

    async def test_prepare_rename_request(self):
        expected_selection = "DataA"
        expected_range_line = 1
        expected_range_character_start = 8
        expected_range_character_end = expected_range_character_start + len(expected_selection)
        res = await self.prepare_rename(TEST_DOCUMENT_NAME, 1, 8)
        actual_range: Range = res.get_range()

        self.assertEqual(actual_range.start.line, expected_range_line)
        self.assertEqual(actual_range.start.character, expected_range_character_start)
        self.assertEqual(actual_range.end.character, expected_range_character_end)

    async def test_prepare_rename_enum_request(self):
        expected_selection = "Options"
        expected_range_line = 19
        expected_range_character_start = 8
        expected_range_character_end = expected_range_character_start + len(expected_selection)
        res = await self.prepare_rename(TEST_DOCUMENT__WITH_ENUM_NAME, 19, 8)
        actual_range: Range = res.get_range()

        self.assertEqual(actual_range.start.line, expected_range_line)
        self.assertEqual(actual_range.start.character, expected_range_character_start)
        self.assertEqual(actual_range.end.character, expected_range_character_end)
    
    async def test_no_prepare_rename_when_nothing_under_cursor(self):
        await self.write_document(TEST_DOCUMENT_NAME, f"\n{TEST_DOCUMENT_CONTENT}")
        res: PrepareRenameResponse = await self.prepare_rename(TEST_DOCUMENT_NAME)
        self.assertIsNone(res.response)
