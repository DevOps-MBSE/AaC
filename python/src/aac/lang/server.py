"""The Architecture-as-Code Language Server."""

import logging

import pygls.lsp.methods as methods

from pygls.lsp import (
    Hover,
    HoverParams,
    InitializeParams,
    InitializeResult,
    ServerCapabilities,
)
from pygls.server import LanguageServer

from aac.plugins.plugin_execution import plugin_result


default_host = "127.0.0.1"
default_port = 8080

# We probably don't want to be doing this here...
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


server = LanguageServer()


def start_lsp(host: str = None, port: int = None):
    """Start the LSP server.

    Arguments:
        host (str): The host on which to listen for LSP requests.
        port (int): The port on which to listen for LSP requests.
    """

    def start(host, port):
        logger.info(f"Starting server at {host}:{port}")
        server.start_ws(host, port)

    connection_details = host or default_host, port or default_port
    with plugin_result("lsp", start, *connection_details) as result:
        result.messages = [m for m in result.messages if m]
        return result


@server.feature(methods.INITIALIZE)
async def handle_initialize(ls: LanguageServer, params: InitializeParams):
    """Handle initialize request."""
    logger.info("received initialize request")

    ls.show_message("received initialize request")

    return InitializeResult(capabilities=ServerCapabilities(hover_provider=True))


@server.feature(methods.INITIALIZED)
async def handle_initialized(ls: LanguageServer, params):
    """Handle initialized notification."""
    logger.info("received initialized notification")

    ls.show_message("received initialized notification")


@server.feature(methods.HOVER)
async def handle_hover(ls: LanguageServer, params: HoverParams):
    """Handle a hover request."""
    logger.info(f"received hover request\nparams are: {params.text_document.uri}")

    ls.show_message("received hover request")
    ls.show_message(
        f"file: {params.text_document.uri}; "
        f"line: {params.position.line}; character: {params.position.character}"
    )

    return Hover(contents="Hello from your friendly AaC LSP server!")
