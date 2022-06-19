from asyncio.tasks import sleep
from typing import Optional
from unittest.async_case import IsolatedAsyncioTestCase

from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.lsp.types.basic_structures import Position, TextDocumentIdentifier, TextDocumentItem, VersionedTextDocumentIdentifier
from pygls.lsp.types.language_features.hover import HoverParams
from pygls.lsp.types.workspace import DidChangeTextDocumentParams, DidCloseTextDocumentParams, DidOpenTextDocumentParams

from tests.base_test_case import BaseTestCase
from tests.helpers.lsp.text_document import TextDocument
from tests.helpers.lsp.responses.hover_response import HoverResponse
from tests.lang.lsp_test_client import LspTestClient


# We have to sleep to give the server enough time to finish processing changes to the active
# context, etc. Just awaiting the send_request function isn't enough since the request will get
# sent and return.
SLEEP_TIME = 1


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
        await sleep(SLEEP_TIME)

        return self.document

    async def close_document(self) -> None:
        """Close the virtual document."""
        assert self.document, "Could not close virtual document because there is no document."

        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_CLOSE,
            DidCloseTextDocumentParams(text_document=TextDocumentIdentifier(uri=self.to_uri(self.document.file_name)))
        )
        await sleep(SLEEP_TIME)

    async def write_document(self, content: str) -> None:
        """
        Write the provided content to the virtual document.

        Args:
            content (str): The content to write to the virtual document.
        """
        assert self.document, "Could not write content to virtual document because there is no document."

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
        await sleep(SLEEP_TIME)

    def read_document(self) -> str:
        """Return the document text."""
        assert self.document, "Could not read content from virtual document because there is no document."
        return self.document.read()

    def to_uri(self, file_name: str) -> Optional[str]:
        """Return file_name as a file URI."""
        return uris.from_fs_path(file_name)

    async def hover(self, file_name: Optional[str] = None, line: int = 0, character: int = 0) -> HoverResponse:
        """Send a hover request and return the response."""
        assert self.document, "Could not hover in virtual document because there is no document."

        hover_response = await self.client.send_request(
            methods.HOVER,
            HoverParams(
                text_document=TextDocumentIdentifier(uri=self.to_uri(file_name or self.document.file_name)),
                position=Position(line=line, character=character),
            )
        )
        await sleep(SLEEP_TIME)
        return HoverResponse(hover_response.result())
