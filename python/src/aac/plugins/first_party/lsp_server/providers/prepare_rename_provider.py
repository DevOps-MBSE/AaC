"""Module for the Prepare Rename Provider which handles requests to prepare symbol rename ranges."""

from typing import Optional
from pygls.server import LanguageServer
from pygls.lsp.types import Range, PrepareRenameParams

from aac.plugins.first_party.lsp_server.providers.symbols import get_symbol_range_at_position
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider


class PrepareRenameProvider(LspProvider):
    """Handles the prepare rename requests."""

    def handle_request(self, language_server: LanguageServer, params: PrepareRenameParams) -> Optional[Range]:
        """
        Return a range that encompasses the symbol or None if the selection is invalid.

        https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_prepareRename

        Args:
            language_server (LanguageServer): An instance of the language server
            params (PrepareRenameParams): PrepareRename request parameters

        Returns:
            A range of consisting of the symbol to rename, or None if it's an invalid symbol
        """
        self.language_server = language_server
        language_server_documents = self.language_server.workspace.documents
        document = language_server_documents.get(params.text_document.uri)
        if document:
            return get_symbol_range_at_position(document.source, params.position.line, params.position.character)
