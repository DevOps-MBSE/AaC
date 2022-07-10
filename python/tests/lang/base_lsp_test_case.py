from typing import Optional
from unittest.async_case import IsolatedAsyncioTestCase

from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.lsp.types.basic_structures import Position, TextDocumentIdentifier, TextDocumentItem, VersionedTextDocumentIdentifier
from pygls.lsp.types.language_features.completion import CompletionContext, CompletionParams, CompletionTriggerKind
from pygls.lsp.types.language_features.hover import HoverParams
from pygls.lsp.types.workspace import DidChangeTextDocumentParams, DidCloseTextDocumentParams, DidOpenTextDocumentParams
from aac.lang.lsp.code_completion_provider import SPACE_TRIGGER

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.lsp.text_document import TextDocument
from tests.helpers.lsp.responses.hover_response import HoverResponse
from tests.helpers.lsp.responses.completion_response import CompletionResponse
from tests.lang.lsp_test_client import LspTestClient


class BaseLspTestCase(ActiveContextTestCase, IsolatedAsyncioTestCase):
    """Base test case providing set up and tear down for LSP tests."""

    documents: dict[str, TextDocument] = {}

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.client = LspTestClient()
        await self.client.start()
        await self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(process_id=12345, capabilities=ClientCapabilities()),
        )

    async def asyncTearDown(self):
        await super().asyncTearDown()
        for file_name in self.documents.keys():
            await self.close_document(file_name)
        self.documents.clear()
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
        assert self.documents.get(file_name) is None, f"Virtual document {file_name} already exists"

        self.documents[file_name] = TextDocument(file_name=file_name, content=content)
        document = self.documents.get(file_name)

        uri = self.to_uri(file_name)
        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_OPEN,
            DidOpenTextDocumentParams(
                text_document=TextDocumentItem(uri=uri, language_id="aac", version=document.version, text=content)
            )
        )

        return document

    async def close_document(self, file_name: str) -> None:
        """
        Close the virtual document.

        Args:
            file_name (str): The name of the file to close.
        """
        assert self.documents.get(file_name), f"Could not close virtual document because there is no document named {file_name}."

        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_CLOSE,
            DidCloseTextDocumentParams(text_document=TextDocumentIdentifier(uri=self.to_uri(file_name)))
        )

    async def write_document(self, file_name: str, content: str) -> None:
        """
        Write the provided content to the virtual document.

        Args:
            file_name (str): The name of the virtual document whose content will be written.
            content (str): The content to write to the virtual document.
        """
        assert self.documents.get(file_name), f"Could not write content to virtual document because there is no document named {file_name}."

        document = self.documents.get(file_name)
        document.version += 1
        document.write(content)
        await self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_CHANGE,
            DidChangeTextDocumentParams(
                text_document=VersionedTextDocumentIdentifier(uri=self.to_uri(file_name), version=document.version),
                content_changes=[{"text": content}]
            )
        )

    def read_document(self, file_name: str) -> str:
        """
        Return the document text.

        Args:
            file_name (str): The name of the virtual document whose content will be read.

        Returns:
            The content of the specified virtual document.
        """
        assert self.documents.get(file_name), f"Could not read content from virtual document because there is no document named {file_name}."
        return self.documents.get(file_name).read()

    def to_uri(self, file_name: str) -> Optional[str]:
        """Return file_name as a file URI."""
        assert self.documents.get(file_name), f"Could not get virtual document URI because there is no document named {file_name}."
        return uris.from_fs_path(file_name)

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
        assert self.documents.get(file_name), f"Could not hover in virtual document because there is no document named {file_name}."

        response = await self.client.send_request(
            methods.HOVER,
            HoverParams(
                text_document=TextDocumentIdentifier(uri=self.to_uri(file_name)),
                position=Position(line=line, character=character),
            )
        )
        return HoverResponse(response.result())

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
        assert self.documents.get(file_name), f"Could not execute code completion in virtual document because there is no document named {file_name}."

        response = await self.client.send_request(
            methods.COMPLETION,
            CompletionParams(
                context=CompletionContext(trigger_kind=trigger_kind, trigger_character=trigger_character),
                text_document=TextDocumentIdentifier(uri=self.to_uri(file_name)),
                position=Position(line=line, character=character),
            )
        )
        return CompletionResponse(response.result())
