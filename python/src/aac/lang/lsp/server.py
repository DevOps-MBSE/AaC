"""The Architecture-as-Code Language Server."""

import logging
from typing import Optional
from pygls.server import LanguageServer
import pygls.lsp.methods as methods

from pygls.lsp import (
    CompletionOptions,
    CompletionParams,
    Hover,
    HoverParams,
    InitializeParams,
    InitializeResult,
    ServerCapabilities,
)

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.language_context import LanguageContext
from aac.lang.lsp.code_completion_provider import CodeCompletionProvider


SERVER: Optional[LanguageServer] = None
ACTIVE_CONTEXT: Optional[LanguageContext] = None
COMPLETION_PROVIDER: Optional[CodeCompletionProvider] = None


def start_lsp():
    """Start the LSP server.

    Args:
        dev (bool): Whether to start the server and setup logging for development. (optional)
    """
    global SERVER, ACTIVE_CONTEXT

    SERVER = SERVER or LanguageServer()
    setup_features(SERVER)
    ACTIVE_CONTEXT = get_active_context()

    logging.info("Starting the AaC LSP server")

    SERVER.start_io()


def setup_features(server: LanguageServer) -> None:
    """Configure the server with the supported features.

    Args:
        server (LanguageServer): The language server for which to configure the available features.
    """
    global COMPLETION_PROVIDER

    @server.feature(methods.INITIALIZE)
    async def handle_initialize(ls: LanguageServer, params: InitializeParams):
        """Handle initialize request."""
        return InitializeResult(capabilities=ServerCapabilities(hover_provider=True))

    @server.feature(methods.HOVER)
    async def handle_hover(ls: LanguageServer, params: HoverParams):
        """Handle a hover request."""
        return Hover(contents="Hello from your friendly AaC LSP server!")

    COMPLETION_PROVIDER = CodeCompletionProvider()
    trigger_and_commit_chars = COMPLETION_PROVIDER.get_trigger_characters()

    @server.feature(methods.COMPLETION, CompletionOptions(trigger_characters=trigger_and_commit_chars))
    async def handle_completion(ls: LanguageServer, params: CompletionParams):
        """Handle a completion request."""
        completion_results = COMPLETION_PROVIDER.handle_code_completion(ls, params)
        logging.debug(f"Completion results: {completion_results}")
        return completion_results
