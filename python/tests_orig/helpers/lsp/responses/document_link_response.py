from pygls.lsp.types import DocumentLink

from tests.helpers.lsp.responses.lsp_response import LspResponse


class DocumentLinkResponse(LspResponse):
    def get_document_links(self) -> list[DocumentLink]:
        """Returns a list of DocumentLink objects from an LSP server response."""
        return [
            DocumentLink(
                range=document_link.get("range"),
                target=document_link.get("target"),
                tooltip=document_link.get("tooltip"),
                data=document_link.get("data"),
            )
            for document_link in self.response
        ]
