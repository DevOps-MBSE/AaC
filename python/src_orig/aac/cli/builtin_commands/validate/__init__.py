"""The validate plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.cli.builtin_commands.validate.validate_impl import validate
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin


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
    validate_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The path to the AaC file to be validated.",
            "file",
        ),
        AacCommandArgument(
            "--definition-name",
            """The name of one definition to validate. (optional)
            This argument will cause only the definition provided by the argument to be validated.""",
            "str",
        ),
    ]

    plugin_commands = [
        AacCommand("validate", "Validate the AaC definition file.", validate, validate_arguments),
    ]

    return plugin_commands
