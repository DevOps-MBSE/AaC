"""The aac-rest-api plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.rest_api.aac_rest_api_impl import rest_api, generate_api_spec


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    return plugin


def _get_plugin_commands():
    rest_api_arguments = [
        AacCommandArgument(
            "--host",
            "Set the hostname of the service. Useful for operating behind proxies.",
            "str",
            default="0.0.0.0",
        ),
        AacCommandArgument(
            "--port",
            "The port to which the RESTful service will be bound.",
            "int",
            default=8080,
        ),
    ]

    generate_api_spec_arguments = [
        AacCommandArgument(
            "output-directory",
            "The output directory in which to write the AaC OpenAPI JSON file",
            "directory",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "rest-api",
            "Start a RESTful interface for interacting with and managing AaC.",
            rest_api,
            rest_api_arguments,
        ),
        AacCommand(
            "generate-openapi-spec",
            "Write the OpenAPI schema to a JSON file.",
            generate_api_spec,
            generate_api_spec_arguments,
        ),
    ]

    return plugin_commands
