"""The Architecture-as-Code Language Server."""

import logging

import pygls.lsp.methods as methods

from pygls.lsp import (
    CompletionItem,
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

from aac.plugins.plugin_execution import plugin_result
from aac.spec.core import get_aac_spec
from aac.util import search


default_host = "127.0.0.1"
default_port = 8080

# We probably don't want to be doing this here...
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


server = LanguageServer()


def start_lsp(host: str = None, port: int = None, dev: bool = False):
    """Start the LSP server.

    Arguments:
        host (str): The host on which to listen for LSP requests.
        port (int): The port on which to listen for LSP requests.
        dev (bool): Whether to start the development (TCP) server.
    """

    def start(host, port):
        if dev:
            logger.info(f"Starting the development server at {host}:{port}")
            server.start_tcp(host, port)
        else:
            logger.info("Starting the production server")
            server.start_io()

    connection_details = host or default_host, port or default_port
    with plugin_result("lsp", start, *connection_details) as result:
        result.messages = [m for m in result.messages if m]
        return result


@server.feature(methods.INITIALIZE)
async def handle_initialize(ls: LanguageServer, params: InitializeParams):
    """Handle initialize request."""
    return InitializeResult(capabilities=ServerCapabilities(hover_provider=True))


@server.feature(methods.HOVER)
async def handle_hover(ls: LanguageServer, params: HoverParams):
    """Handle a hover request."""
    return Hover(contents="Hello from your friendly AaC LSP server!")


@server.feature(methods.COMPLETION, CompletionOptions(trigger_characters=[], all_commit_characters=[":"]))
async def handle_completion(ls: LanguageServer, params: CompletionParams):
    """Handle a completion request."""
    data, _ = get_aac_spec()
    fields = search(data, ["root", "data", "fields"])
    return CompletionList(is_incomplete=False, items=[
        CompletionItem(
            label=f.get("name"),
            documentation=f.get("description"),
        ) for f in fields
    ])
