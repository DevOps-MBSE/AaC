from unittest.async_case import IsolatedAsyncioTestCase
from pygls.lsp import methods
from pygls.lsp.types import RenameParams
from aac.io.constants import DEFINITION_SEPARATOR
from aac.lang.constants import DEFINITION_NAME_ROOT

from tests.helpers.lsp.responses.rename_response import RenameResponse
from tests.helpers.parsed_definitions import create_definition, create_field_entry, create_schema_definition, create_schema_ext_definition
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_CONTENT,
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_WITH_ENUM_NAME,
    TEST_DOCUMENT_WITH_ENUM_CONTENT,
)


class TestRenameProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def rename(self, file_name: str, new_name: str, line: int = 0, character: int = 0) -> RenameResponse:
        """
        Send a rename request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the hover action.
            line (int): The line number (starting from 0) at which to perform the hover action.
            character (int): The character number (starting from 0) at which to perform the hover action.
            new_name (str): The new name to apply.

        Returns:
            A RenameResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            RenameResponse,
            methods.RENAME,
            RenameParams(**self.build_text_document_position_params(file_name, line, character), new_name=new_name),
        )

    async def test_rename_request(self):
        expected_new_name = "DataANew"
        res: RenameResponse = await self.rename(TEST_DOCUMENT_NAME, expected_new_name, 1, 8)
        actual_text_edits = res.get_all_text_edits()
        actual_document_edits = res.get_workspace_edit()
        self.assertIn(TEST_DOCUMENT_NAME, list(actual_document_edits.keys())[0])
        self.assertIn(expected_new_name, actual_text_edits[0].get("newText"))
        self.assertEqual(2, len(actual_text_edits))

    async def test_rename_enum_request(self):
        expected_new_enum = "ONE"
        await self.create_document(TEST_DOCUMENT_WITH_ENUM_NAME, f"\n{TEST_DOCUMENT_WITH_ENUM_CONTENT}")
        res: RenameResponse = await self.rename(TEST_DOCUMENT_WITH_ENUM_NAME, expected_new_enum, 31, 14)
        actual_text_edits = res.get_all_text_edits()
        actual_test_document_edits = res.get_workspace_edit()
        self.assertIn(TEST_DOCUMENT_WITH_ENUM_NAME, list(actual_test_document_edits.keys())[0])
        self.assertIn(expected_new_enum, actual_text_edits[0].get("newText"))
        self.assertEqual(2, len(actual_text_edits))

    async def test_rename_root_key_request(self):
        root_key_to_change_name = "NewKey"
        root_key_to_change = "new_key"
        updated_root_key = "New_Key"
        root_key_schema_field = create_field_entry("field1", "string")
        new_root_key_definition = create_schema_definition(root_key_to_change_name, "", [root_key_schema_field])
        new_root_ext_field = create_field_entry(root_key_to_change, root_key_to_change_name)
        root_key_extension = create_schema_ext_definition("newRootExt", DEFINITION_NAME_ROOT, fields=[new_root_ext_field])
        test_key_instance = create_definition(root_key_to_change, "NewKeyInstance", {"field1": "test"})

        test_definitions = [new_root_key_definition, root_key_extension, test_key_instance]
        test_file_content = DEFINITION_SEPARATOR.join([f"{definition.to_yaml()}" for definition in test_definitions])

        test_document_name = "test_me.aac"
        await self.create_document(test_document_name, test_file_content)
        res: RenameResponse = await self.rename(test_document_name, updated_root_key, 18, 0)

        actual_text_edits = res.get_all_text_edits()
        actual_test_document_edits = res.get_workspace_edit()
        self.assertIsNotNone(res.response)
        self.assertIn(test_document_name, list(actual_test_document_edits.keys())[0])
        self.assertIn(updated_root_key, actual_text_edits[0].get("newText"))

    async def test_no_rename_when_nothing_under_cursor(self):
        expected_new_name = "DataANew"
        await self.write_document(TEST_DOCUMENT_NAME, f"\n{TEST_DOCUMENT_CONTENT}")
        res: RenameResponse = await self.rename(TEST_DOCUMENT_NAME, expected_new_name)
        self.assertIsNone(res.response)

    async def test_rename_request_doesnt_duplicate_colons(self):
        """Covers bugfix #597."""
        lsp_client_new_text = "DataANew:"
        expected_new_name = lsp_client_new_text.strip(":")

        res: RenameResponse = await self.rename(TEST_DOCUMENT_NAME, lsp_client_new_text, 1, 8)
        actual_text_edits = res.get_all_text_edits()
        actual_document_edits = res.get_workspace_edit()

        self.assertIn(TEST_DOCUMENT_NAME, list(actual_document_edits.keys())[0])
        self.assertEqual(expected_new_name, actual_text_edits[0].get("newText"))
        self.assertEqual(2, len(actual_text_edits))
