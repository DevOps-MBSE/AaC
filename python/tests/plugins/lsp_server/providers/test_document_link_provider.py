from os import path
from unittest.async_case import IsolatedAsyncioTestCase

from pygls.uris import from_fs_path
from pygls.lsp import methods
from pygls.lsp.types import DocumentLinkParams

from tests.helpers.lsp.responses.document_link_response import DocumentLinkResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_NAME,
    TEST_SCHEMA_C
)


class TestDocumentLinksProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def request(self, text_document: str) -> DocumentLinkResponse:
        """
        Send a document links request and return the response.

        Args:
            text_document (str): The name of the virtual document in which to perform the document link action.

        Returns:
            A FindReferencesResponse that is returned from the LSP server.
        """
        return await self.build_request(
            text_document,
            DocumentLinkResponse,
            methods.DOCUMENT_LINK,
            DocumentLinkParams(
                text_document={"uri": text_document}
            ),
        )

    async def test_document_link_provider(self):
        test_schema_definition = TEST_SCHEMA_C.copy()
        test_schema_definition.imports = [f"./{TEST_DOCUMENT_NAME}"]
        new_file_name = "new.aac"
        await self.create_document(new_file_name, test_schema_definition.to_yaml())
        new_file_path = path.join(self.temp_documents_directory.name, new_file_name)

        res: DocumentLinkResponse = await self.request(
            text_document=new_file_path
        )

        document_links = res.get_document_links()
        expected_link = from_fs_path(path.join(self.temp_documents_directory.name, TEST_DOCUMENT_NAME))
        self.assertIsNotNone(document_links)
        self.assertEqual(expected_link, document_links[0].target)
        self.assertEqual(1, document_links[0].range.start.line)
        self.assertEqual(1, document_links[0].range.end.line)
