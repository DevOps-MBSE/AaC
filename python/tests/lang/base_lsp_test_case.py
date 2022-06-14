from typing import Optional
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


class BaseLspTestCase(BaseTestCase):
    """Base test case providing set up and tear down for LSP tests."""

    document: Optional[TextDocument] = None

    def setUp(self) -> None:
        super().setUp()

        self.client = LspTestClient()
        self.client.start()
        res = self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(process_id=12345, root_uri=self.to_uri("root.aac"), capabilities=ClientCapabilities()),
        )

        self.assertIn("capabilities", res)

    def tearDown(self):
        self.close_document()
        self.client.stop()

    def create_document(self, file_name: str, content: str = "") -> TextDocument:
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
        self.client.send_notification(
            methods.TEXT_DOCUMENT_DID_OPEN,
            DidOpenTextDocumentParams(
                text_document=TextDocumentItem(uri=uri, language_id="aac", version=self.document.version, text=content)
            )
        )

        return self.document

    def close_document(self) -> None:
        """Close the virtual document."""
        if self.document:
            self.client.send_notification(
                methods.TEXT_DOCUMENT_DID_CLOSE,
                DidCloseTextDocumentParams(text_document=TextDocumentIdentifier(uri=self.to_uri(self.document.file_name)))
            )
        else:
            raise LspTestCaseError("Could not close virtual document because there is no document.")

    def write_document(self, content: str) -> None:
        """
        Write the provided content to the virtual document.

        Args:
            content (str): The content to write to the virtual document.
        """
        if self.document:
            self.document.version += 1
            self.document.write(content)
            self.client.send_notification(
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


@attrs(slots=True)
class LspTestCaseError(RuntimeError):
    """An error caused by an issue with the test case."""

    message: str = attrib(validator=instance_of(str))
