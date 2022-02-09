"""The Architecture-as-Code Language Server."""

import logging
import pygls.lsp.methods as methods

from pygls.server import LanguageServer

from aac.plugins.plugin_execution import plugin_result

default_host = "127.0.0.1"
default_port = 8080

# We probably don't want to be doing this here...
logging.basicConfig(level=logging.DEBUG)


class AacLanguageServer(LanguageServer):
    """A language server for the AaC requests."""

    def __init__(self, loop=None):
        """Create a new instance of an AaC Language Server."""
        super().__init__(loop)


server = AacLanguageServer()


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


@server.feature(methods.HOVER)
async def handle_hover(ls: LanguageServer, params):
    """Handle a hover event."""
    ls.show_message("received hover request")
