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
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result


LOGGER: Optional[logging.Logger] = None
SERVER: Optional[LanguageServer] = None
ACTIVE_CONTEXT: Optional[LanguageContext] = None
COMPLETION_PROVIDER: Optional[CodeCompletionProvider] = None


def start_lsp(dev: bool = False) -> PluginExecutionResult:
    """Start the LSP server.

    Args:
        dev (bool): Whether to start the server and setup logging for development. (optional)
    """

    def start():
        global SERVER, LOGGER, ACTIVE_CONTEXT

        SERVER = SERVER or LanguageServer()
        setup_features(SERVER)
        ACTIVE_CONTEXT = get_active_context()

        _setup_logger(logging.DEBUG if dev else logging.INFO)
        LOGGER.info("Starting the AaC LSP server")

        SERVER.start_io()

    with plugin_result("lsp", start) as result:
        result.messages = [m for m in result.messages if m]
        return result


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


def _setup_logger(log_level: int) -> None:
    """Configure the logger.

    Args:
        log_level (int): The logging level to use for the logger.
    """
    global LOGGER
    logging.basicConfig(level=log_level)
    LOGGER = logging.getLogger(__name__)
