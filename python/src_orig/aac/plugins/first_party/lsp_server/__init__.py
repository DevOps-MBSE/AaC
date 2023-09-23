"""The start-lsp plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.lsp_server.start_lsp_server_impl import start_lsp_io, start_lsp_tcp, plugin_name


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    return plugin


def _get_plugin_commands():
    start_lsp_tcp_arguments = [
        AacCommandArgument(
            "--host",
            "The host address to bind the TCP server to.",
            "str",
            default="127.0.0.1",
        ),
        AacCommandArgument(
            "--port",
            "The host port to bing the TCP server to.",
            "int",
            default=5007,
        ),
    ]

    plugin_commands = [
        AacCommand(
            "start-lsp-io",
            "Start the AaC Language Server Protocol (LSP) server in IO mode.",
            start_lsp_io,
        ),
        AacCommand(
            "start-lsp-tcp",
            "Start the AaC Language Server Protocol (LSP) server in TCP mode.",
            start_lsp_tcp,
            start_lsp_tcp_arguments,
        ),
    ]

    return plugin_commands
