"""The active-context plugin module."""

from aac.execute.plugin_runner import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.active_context.active_context_impl import (
    plugin_name,
    list_files,
    list_definitions,
    describe_definition,
    import_state,
    export_state,
)


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
    describe_definition_arguments = [
        AacCommandArgument(
            "definition-name",
            "The name of a defintion in the active context.",
            "str",
        ),
    ]
    import_state_arguments = [
        AacCommandArgument(
            "state-file",
            "The persistent state file from which to get information about how to configure the active context.",
            "str",
        ),
    ]
    export_state_arguments = [
        AacCommandArgument(
            "state-file-name",
            "The name of the state file in which to export the current active context.",
            "str",
        ),
        AacCommandArgument(
            "overwrite",
            "A flag indicating that the state file should be overwritten, if it exists.",
            "bool",
            default=False,
        ),
    ]

    plugin_commands = [
        AacCommand(
            "list-files",
            "Display the files in the active context.",
            list_files,
        ),
        AacCommand(
            "list-definitions",
            "List all definitions within the active context.",
            list_definitions,
        ),
        AacCommand(
            "describe-definition",
            "Describe a definition in the active context.",
            describe_definition,
            describe_definition_arguments,
        ),
        AacCommand(
            "import-state",
            "Configure the active context to be initialized with the definitions, plugins, etc from a state file.",
            import_state,
            import_state_arguments,
        ),
        AacCommand(
            "export-state",
            "Export the current active context to a state file.",
            export_state,
            export_state_arguments,
        ),
    ]

    return plugin_commands
