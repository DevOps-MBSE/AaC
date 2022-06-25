from typing import Optional
from unittest.async_case import IsolatedAsyncioTestCase

from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.lsp.types.basic_structures import Model, Position, TextDocumentIdentifier, TextDocumentItem, VersionedTextDocumentIdentifier
from pygls.lsp.types.text_synchronization import TextDocumentSyncKind
from pygls.lsp.types.workspace import DidChangeTextDocumentParams, DidCloseTextDocumentParams, DidOpenTextDocumentParams
from pygls.workspace import Document

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.lsp.text_document import TextDocument
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
        self.active_context = self.client.server.language_context
        await self.create_document(TEST_DOCUMENT_NAME, TEST_DOCUMENT_CONTENT)

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

    def virtual_document_to_lsp_document(self, file_name: str) -> Document:
        """Convert a virtual document to an LSP document."""
        assert self.documents.get(file_name), f"Could not convert virtual document because there is no document named {file_name}."
        document = self.documents.get(file_name)
        return Document(uri=document.file_name, source=document.content, version=document.version, sync_kind=TextDocumentSyncKind.FULL)

    def build_text_document_position_params(self, file_name: str, line: int = 0, character: int = 0) -> dict:
        """Return a dictionary that can be used as TextDocumentPositionParams in an LSP request."""
        return {
            "text_document": TextDocumentIdentifier(uri=self.to_uri(file_name)),
            "position": Position(line=line, character=character),
        }

    async def build_request(self, file_name: str, response_type: type, method: str, params: Model):
        self.assertIsNotNone(
            self.documents.get(file_name),
            f"Could not execute {method} in virtual document because there is no document named {file_name}."
        )
        response = await self.client.send_request(method, params)
        return response_type(response.result())


TEST_DOCUMENT_NAME = "test.aac"
TEST_DOCUMENT_MODEL_NAME = "ServiceOne"
TEST_DOCUMENT_SCHEMA_NAME = "DataA"
TEST_ADDITIONAL_SCHEMA_NAME = "DataC"
TEST_ADDITIONAL_MODEL_NAME = "ServiceTwo"
TEST_DOCUMENT_CONTENT = f"""
schema:
  name: {TEST_DOCUMENT_SCHEMA_NAME}
  fields:
  - name: msg
    type: string
---
schema:
  name: DataB
  fields:
  - name: msg
    type: string
---
model:
  name: {TEST_DOCUMENT_MODEL_NAME}
  behavior:
    - name: Process DataA Request
      type: request-response
      description: Process a DataA request and return a DataB response
      input:
        - name: in
          type: {TEST_DOCUMENT_SCHEMA_NAME}
      output:
        - name: out
          type: DataB
      acceptance:
        - scenario: Receive DataA request and return DataB response
          given:
            - ServiceOne is running
          when:
            - ServiceOne receives a DataA request
          then:
            - ServiceOne processes the request into a DataB response
            - ServiceOne returns the DataB response
        - scenario: Receive invalid request
          given:
            - ServiceOne is running
          when:
            - ServiceOne receives request that isn't a DataA request
          then:
            - ServiceOne returns an error response code
"""
TEST_DOCUMENT_ADDITIONAL_CONTENT = f"""
schema:
  name: {TEST_ADDITIONAL_SCHEMA_NAME}
  fields:
  - name: msg
    type: string
---
model:
  name: {TEST_ADDITIONAL_MODEL_NAME}
  behavior:
    - name: Process DataB Request
      type: request-response
      description: Process a DataB request and return a DataC response
      input:
        - name: in
          type: DataB
      output:
        - name: out
          type: DataC
      acceptance:
        - scenario: Receive DataB request and return DataC response
          given:
            - ServiceTwo is running
          when:
            - ServiceTwo receives a DataB request
          then:
            - ServiceTwo processes the request into a DataC response
            - ServiceTwo returns the DataC response
"""
TEST_PARTIAL_CONTENT = f"""
schema:
  name: {TEST_ADDITIONAL_SCHEMA_NAME}
  fields:
  - name: msg
    type:\
"""
TEST_ADDITIONAL_MODEL_CONTENT = f"""
model:
  name: ServiceThree
  behavior:
    - name: Pass through
      type: request-response
      input:
        - name: in
          type: {TEST_ADDITIONAL_SCHEMA_NAME}
      output:
        - name: out
          type: {TEST_ADDITIONAL_SCHEMA_NAME}
      acceptance:
        - scenario: Pass the data through, untouched
          when:
            - ServiceThree receives a {TEST_ADDITIONAL_SCHEMA_NAME} request
          then:
            - ServiceThree returns the {TEST_ADDITIONAL_SCHEMA_NAME} data in the response, untouched
"""
