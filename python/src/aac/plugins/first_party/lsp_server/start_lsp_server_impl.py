"""AaC Plugin implementation module for the start-lsp plugin."""

from typing import Callable
from aac.plugins.first_party.lsp_server.language_server import AacLanguageServer
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "start-lsp"


def start_lsp_io():
    """Start the LSP server in IO mode."""
    aac_language_server = AacLanguageServer()
    return _start_lsp(aac_language_server.start_io)


def start_lsp_tcp(host: str = "127.0.0.1", port: int = 5007):
    """
    Start the LSP server in TCP mode.

    Args:
        host (str): The host address to bind the TCP server to.
        port (int): The host port to bing the TCP server to.
    """
    aac_language_server = AacLanguageServer()
    function_kwargs = {"host": host, "port": port}
    return _start_lsp(aac_language_server.start_tcp, **function_kwargs)


def _start_lsp(language_server_start_function: Callable, **start_function_kwargs) -> PluginExecutionResult:
    """Start the LSP server."""
    with plugin_result(plugin_name, language_server_start_function, **start_function_kwargs) as result:
        result.messages = [m for m in result.messages if m]
        return result
