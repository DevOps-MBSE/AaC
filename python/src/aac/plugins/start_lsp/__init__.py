"""The start-lsp plugin module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.start_lsp.start_lsp_impl import start_lsp_io, start_lsp_tcp

plugin_resource_file_args = (__package__, "start-lsp.yaml")


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    This function is automatically generated. Do not edit.

    Returns:
        list of AacCommands
    """
    start_lsp_tcp_arguments = [
        AacCommandArgument(
            "--host",
            "The host address to bind the TCP server to. Defaults to 127.0.0.1.",
        ),
        AacCommandArgument(
            "--port",
            "The host port to bing the TCP server to. Defaults to 5007.",
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


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns the information about plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_commands(set(get_commands()))

    return plugin
