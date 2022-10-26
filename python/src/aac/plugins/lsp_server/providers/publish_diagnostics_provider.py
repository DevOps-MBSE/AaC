"""Module for PublishDiagnostics Provider which handles publishing of diagnostics for AaC Language Server."""

from pygls.server import LanguageServer
from pygls.lsp.types.diagnostics import PublishDiagnosticsParams
from pygls.lsp.types.basic_structures import Position, Range
from pygls.lsp import (
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
)
from pygls.lsp.types.basic_structures import Diagnostic

from aac.plugins.lsp_server.providers.lsp_provider import LspProvider


class PublishDiagnosticsProvider(LspProvider):
    """Handler for Publishing Diagnostics for AaC LSP."""
    ls = LanguageServer

    async def diagnostic_did_open(self, ls: LanguageServer, doc_params: DidOpenTextDocumentParams, params: PublishDiagnosticsParams) -> None:

        ls.show_message("Validating AaC Open AaC File...")
        file = ls.workspace.get_document(doc_params.text_document.uri)
        diagnostics = Diagnostic(
            range=Range(
                start=Position(line=1, character=1),
                end=Position(line=1, character=""),
            ),
            message=f"Validating {file}...",
            source="AaC Language Server"
        ),
        ls.publish_diagnostics(file.uri, [diagnostics])

    async def diagnostic_did_change(self, ls: LanguageServer, doc_params: DidChangeTextDocumentParams, params: PublishDiagnosticsParams) -> None:
        ls.show_message("Validating AaC Changes in AaC File...")
        file = ls.workspace.get_document(doc_params.text_document.uri)
        diagnostics = Diagnostic(
            range=Range(
                start=Position(line=1, character=1),
                end=Position(line=1, character="")
            ),
            message=f"Validating {file}...",
            source="AaC Language Server"
        ),
        ls.publish_diagnostics(file.uri, [diagnostics])
