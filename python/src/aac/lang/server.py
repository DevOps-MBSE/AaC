"""The Architecture-as-Code Language Server."""

from pygls.server import LanguageServer
import pygls.lsp.methods as methods

from pygls.lsp import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    Hover,
    HoverParams,
    InitializeParams,
    InitializeResult,
    ServerCapabilities,
)

from aac.lang.active_context_lifecycle_manager import get_active_context


def setup_features(server: LanguageServer) -> None:
    """Configure the server with the supported features.

    Args:
        server (LanguageServer): The language server for which to configure the available features.
    """

    @server.feature(methods.INITIALIZE)
    async def handle_initialize(ls: LanguageServer, params: InitializeParams):
        """Handle initialize request."""
        return InitializeResult(capabilities=ServerCapabilities(hover_provider=True))

    @server.feature(methods.HOVER)
    async def handle_hover(ls: LanguageServer, params: HoverParams):
        """Handle a hover request."""
        return Hover(contents="Hello from your friendly AaC LSP server!")

    @server.feature(methods.COMPLETION, CompletionOptions(all_commit_characters=[":"]))
    async def handle_completion(ls: LanguageServer, params: CompletionParams):
        """Handle a completion request."""
        root_fields = get_active_context().get_root_fields()
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(
                    label=root_field.get("name"),
                    kind=CompletionItemKind.Struct,
                    documentation=root_field.get("description"),
                    commit_characters=[":"],
                )
                for root_field in root_fields
            ],
        )
