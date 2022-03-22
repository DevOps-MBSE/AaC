"""The Architecture-as-Code Language Server."""

import logging
from typing import Optional

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
from pygls.server import LanguageServer

from aac.spec import get_root_fields
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result


logger: Optional[logging.Logger] = None
server: Optional[LanguageServer] = None


def start_lsp(dev: bool = False) -> PluginExecutionResult:
    """Start the LSP server.

    Args:
        dev (bool): Whether to start the server and setup logging for development. (optional)
    """

    def start():
        global server, logger

        server = server or LanguageServer()
        setup_features(server)

        _setup_logger(logging.DEBUG if dev else logging.INFO)
        logger.info("Starting the AaC LSP server")

        server.start_io()

    with plugin_result("lsp", start) as result:
        result.messages = [m for m in result.messages if m]
        return result


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
        root_keys = get_root_fields()
        return CompletionList(
            is_incomplete=False,
            items=[
                CompletionItem(
                    label=root_key.get("name"),
                    kind=CompletionItemKind.Struct,
                    documentation=root_key.get("description"),
                    commit_characters=[":"],
                )
                for root_key in root_keys
            ],
        )


def _setup_logger(log_level: int) -> None:
    """Configure the logger.

    Args:
        log_level (int): The logging level to use for the logger.
    """
    global logger
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
