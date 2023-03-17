from os import path
from tempfile import TemporaryDirectory
from unittest.async_case import IsolatedAsyncioTestCase

from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.lsp.types.basic_structures import (
    Model,
    Position,
    TextDocumentIdentifier,
    TextDocumentItem,
    VersionedTextDocumentIdentifier,
)
from pygls.lsp.types.text_synchronization import TextDocumentSyncKind
from pygls.lsp.types.workspace import DidChangeTextDocumentParams, DidCloseTextDocumentParams, DidOpenTextDocumentParams
from pygls.workspace import Document

from aac.spec import core

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.lsp.text_document import TextDocument
from tests.plugins.lsp_server.definition_constants import TEST_DOCUMENT_CONTENT, TEST_DOCUMENT_NAME
from tests.plugins.lsp_server.lsp_test_client import LspTestClient


class BaseLspTestCase(ActiveContextTestCase, IsolatedAsyncioTestCase):
    """Base test case providing set up and tear down for LSP tests."""

    documents: dict[str, TextDocument] = {}

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.client = LspTestClient()
        self.active_context = self.client.server.language_context
        self.temp_documents_directory: TemporaryDirectory = TemporaryDirectory()

        await self.client.start()
        await self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(capabilities=ClientCapabilities(), root_uri=self.temp_documents_directory.name),
        )

        # Add the core spec to the virtual docs
        core_spec_virtual_doc = self._create_core_spec_virtual_doc()
        self.documents[core_spec_virtual_doc.get_full_path()] = core_spec_virtual_doc

        await self.create_document(TEST_DOCUMENT_NAME, TEST_DOCUMENT_CONTENT)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        self.documents.clear()
        self.temp_documents_directory.cleanup()
        await self.client.stop()

    async def create_document(self, file_name: str, content: str = "") -> TextDocument:
        """
        Create a virtual document with the provided contents.

        Args:
            file_name (str): The name of the file for the virtual document.
            content (str): The contents to write to the virtual document.

        Returns:
            The new virtual document
        """
        absolute_file_path = self._get_absolute_file_path(file_name)
        self.assertIsNone(self.documents.get(absolute_file_path), f"Virtual document {file_name} already exists")

        self.documents[absolute_file_path] = TextDocument(
            file_path=path.dirname(absolute_file_path), file_name=file_name, content=content
        )
        document = self.documents.get(absolute_file_path)

        uri = self.to_uri(absolute_file_path)
        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_OPEN,
            DidOpenTextDocumentParams(
                text_document=TextDocumentItem(uri=uri, language_id="aac", version=document.version, text=content)
            ),
        )

        return document

    async def close_document(self, file_name: str) -> None:
        """
        Close the virtual document.

        Args:
            file_name (str): The name of the file to close.
        """
        absolute_file_path = self._get_absolute_file_path(file_name)
        self.assertIsNotNone(
            self.documents.get(absolute_file_path),
            f"Could not close virtual document because there is no document named {absolute_file_path}.",
        )

        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_CLOSE,
            DidCloseTextDocumentParams(text_document=TextDocumentIdentifier(uri=self.to_uri(absolute_file_path))),
        )

    async def write_document(self, file_name: str, content: str) -> None:
        """
        Write the provided content to the virtual document.

        Args:
            file_name (str): The name of the virtual document whose content will be written.
            content (str): The content to write to the virtual document.
        """
        absolute_file_path = self._get_absolute_file_path(file_name)
        document = self.documents.get(absolute_file_path)
        self.assertIsNotNone(
            document, f"Could not write content to virtual document because there is no document named {absolute_file_path}."
        )

        document.version += 1
        document.write(content)
        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_CHANGE,
            DidChangeTextDocumentParams(
                text_document=VersionedTextDocumentIdentifier(uri=self.to_uri(absolute_file_path), version=document.version),
                content_changes=[{"text": content}],
            ),
        )

    def read_document(self, file_name: str) -> str:
        """
        Return the document text.

        Args:
            file_name (str): The name of the virtual document whose content will be read.

        Returns:
            The content of the specified virtual document.
        """
        absolute_file_path = self._get_absolute_file_path(file_name)
        self.assertIsNotNone(
            self.documents.get(absolute_file_path),
            f"Could not read content from virtual document because there is no document named {absolute_file_path}.",
        )
        return self.documents.get(absolute_file_path).read()

    def to_uri(self, file_name: str) -> str:
        """Return file_name as a file URI."""
        absolute_file_path = self._get_absolute_file_path(file_name)
        self.assertIsNotNone(
            self.documents.get(absolute_file_path),
            f"Could not get virtual document URI because there is no document named {absolute_file_path}.",
        )
        return uris.from_fs_path(absolute_file_path) or absolute_file_path

    def virtual_document_to_lsp_document(self, file_name: str) -> Document:
        """Convert a virtual document to an LSP document."""
        absolute_file_path = self._get_absolute_file_path(file_name)
        self.assertIsNotNone(
            self.documents.get(absolute_file_path),
            f"Could not convert virtual document because there is no document named {absolute_file_path}.",
        )
        document = self.documents.get(absolute_file_path)
        return Document(
            absolute_file_path, source=document.content, version=document.version, sync_kind=TextDocumentSyncKind.FULL
        )

    def build_text_document_position_params(self, file_name: str, line: int = 0, character: int = 0) -> dict:
        """
        Return a dictionary that can be used as TextDocumentPositionParams in an LSP request.

        Returns:
            A dictionary with the `text_document` and `position` attributes.
        """
        absolute_file_path = self._get_absolute_file_path(file_name)
        return {
            "text_document": TextDocumentIdentifier(uri=self.to_uri(absolute_file_path)),
            "position": Position(line=line, character=character),
        }

    async def build_request(self, file_name: str, response_type: type, method: str, params: Model):
        absolute_file_path = self._get_absolute_file_path(file_name)
        self.assertIsNotNone(
            self.documents.get(absolute_file_path),
            f"Could not execute {method} in virtual document because there is no document named {absolute_file_path}.",
        )
        response = await self.client.send_request(method, params)
        return response_type(response.result())

    def _get_absolute_file_path(self, file_name: str):
        return path.realpath(path.join(self.temp_documents_directory.name, file_name))

    def _create_core_spec_virtual_doc(self) -> TextDocument:
        content = core.get_aac_spec_as_yaml()
        full_file_path = core._get_aac_spec_file_path()
        return TextDocument(file_path=path.dirname(full_file_path), file_name=path.basename(full_file_path), content=content)
