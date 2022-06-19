from typing import Optional
from unittest.async_case import IsolatedAsyncioTestCase
from attr import attrib, attrs
from attr.validators import instance_of

from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.lsp.types.basic_structures import Position, TextDocumentIdentifier, TextDocumentItem, VersionedTextDocumentIdentifier
from pygls.lsp.types.language_features.hover import HoverParams
from pygls.lsp.types.workspace import DidChangeTextDocumentParams, DidCloseTextDocumentParams, DidOpenTextDocumentParams

from tests.base_test_case import BaseTestCase
from tests.helpers.lsp.text_document import TextDocument
from tests.lang.lsp_test_client import LspTestClient


class BaseLspTestCase(BaseTestCase, IsolatedAsyncioTestCase):
    """Base test case providing set up and tear down for LSP tests."""

    document: Optional[TextDocument] = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.client = LspTestClient()
        await self.client.start()
        await self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(process_id=12345, root_uri=self.to_uri("root.aac"), capabilities=ClientCapabilities()),
        )

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.close_document()
        await self.client.stop()

    async def create_document(self, file_name: str, content: str = "") -> TextDocument:
        """
        Create a virtual document with the provided contents.

        Args:
            file_name (str): The name of the file for the virtual document.
            content (str): The contents to write to the virtual document.

        Returns:
            The virtual document
        """
        self.document = TextDocument(file_name=file_name, content=content)

        uri = self.to_uri(file_name)
        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_OPEN,
            DidOpenTextDocumentParams(
                text_document=TextDocumentItem(uri=uri, language_id="aac", version=self.document.version, text=content)
            )
        )

        return self.document

    async def close_document(self) -> None:
        """Close the virtual document."""
        if self.document:
            await self.client.send_notification(
                methods.TEXT_DOCUMENT_DID_CLOSE,
                DidCloseTextDocumentParams(text_document=TextDocumentIdentifier(uri=self.to_uri(self.document.file_name)))
            )
        else:
            raise LspTestCaseError("Could not close virtual document because there is no document.")

    async def write_document(self, content: str) -> None:
        """
        Write the provided content to the virtual document.

        Args:
            content (str): The content to write to the virtual document.
        """
        if self.document:
            self.document.version += 1
            self.document.write(content)
            await self.client.send_notification(
                methods.TEXT_DOCUMENT_DID_CHANGE,
                DidChangeTextDocumentParams(
                    text_document=VersionedTextDocumentIdentifier(
                        uri=self.to_uri(self.document.file_name), version=self.document.version
                    ),
                    content_changes=[{"text": content}]
                )
            )
        else:
            raise LspTestCaseError("Could not write content to virtual document because there is no document.")

    def read_document(self) -> str:
        """Return the document text."""
        if self.document:
            return self.document.read()
        raise LspTestCaseError("Could not read content from virtual document because there is no document.")

    def to_uri(self, file_name: str) -> Optional[str]:
        """Return file_name as a file URI."""
        return uris.from_fs_path(file_name)

    async def hover(self, file_name: str, line: int = 0, character: int = 0):
        """Send a hover request and return the response."""
        hover_response = await self.client.send_request(
            methods.HOVER,
            HoverParams(
                text_document=TextDocumentIdentifier(uri=self.to_uri(file_name)),
                position=Position(line=line, character=character),
            )
        )
        return hover_response.result()


@attrs(slots=True)
class LspTestCaseError(RuntimeError):
    """An error caused by an issue with the test case."""

    message: str = attrib(validator=instance_of(str))
