"""The Architecture-as-Code Language Server."""

import logging
import pygls.lsp.methods as methods

from pygls.server import LanguageServer
from pygls.lsp.types import InitializeResult, ServerCapabilities

from aac.plugins.plugin_execution import plugin_result

default_host = "127.0.0.1"
default_port = 8080

# We probably don't want to be doing this here...
logging.basicConfig(level=logging.DEBUG)


server = LanguageServer()


def start_lsp(host: str = None, port: int = None):
    """Start the LSP server.

    Arguments:
        host (str): The host on which to listen for LSP requests.
        port (int): The port on which to listen for LSP requests.
    """

    def start(host, port):
        server.start_tcp(host, port)

    connection_details = host or default_host, port or default_port
    with plugin_result("lsp", start, *connection_details) as result:
        result.messages = [m for m in result.messages if m]
        return result


@server.feature(methods.INITIALIZE)
def handle_initialize(ls: LanguageServer, params):
    """Handle an initialize request."""
    ls.show_message_log("received initialize request")
    ls.show_message_log(f"params: {params}")
    return InitializeResult(
        capabilities=ServerCapabilities(hoverProvider=True),
        serverInfo={"name": "aac-server"},
    )


@server.feature(methods.INITIALIZED)
def handle_initialized(ls: LanguageServer, params):
    """Handle an initialized notification."""
    ls.show_message("received initialized notification")
    ls.show_message_log(f"params: {params}")
    return None


@server.feature(methods.HOVER)
def handle_hover(ls: LanguageServer, params):
    """Handle a hover event."""
    ls.show_message("received hover request")
    ls.show_message_log(f"params: {params}")
