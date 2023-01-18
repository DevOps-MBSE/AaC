"""AaC Plugin implementation module for the active-context plugin."""

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "active-context"


def list_files() -> PluginExecutionResult:
    """
    Display the files in the active context.

    Returns:
        files Files that are in the active context.
    """

    def collect_files() -> str:
        return "\n".join([file.uri for file in get_active_context().get_files_in_context()])

    with plugin_result(plugin_name, collect_files) as result:
        return result


def remove_file(file: str) -> PluginExecutionResult:
    """
    Remove a file from the active context.

    Args:
        file (str): The name of the file that is being removed from the active context.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("remove_file is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def add_file(file: str) -> PluginExecutionResult:
    """
    Add a file to the active context.

    Args:
        file (str): The name of the file to add to the active context.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("add_file is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def reset_context() -> PluginExecutionResult:
    """Reset the active context to a fresh state before any changes have been made."""
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("reset_context is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def list_definitions() -> PluginExecutionResult:
    """
    List all definitions within the active context.

    Returns:
        definitions The list of all definitions that are in the active context.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("list_definitions is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def describe_definition(definition_name: str) -> PluginExecutionResult:
    """
    Describe a definition in the active context.

    Args:
        definition_name (str): The name of a defintion in the active context.

    Returns:
        definition_structure The YAML representation of the structure of the definition.
        definition_source The source file of the definition in the active context.
        definition_start The line on which the definition starts in {{active-context.describe-definition.output.definition-source}}.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("describe_definition is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def import_state(state_file: str) -> PluginExecutionResult:
    """
    Configure the active context to be initialized with the definitions, plugins, etc from a state file.

    Args:
        state_file (str): The persistent state file from which to get information about how to configure the active context.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("import_state is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result


def export_state(state_file_name: str, overwrite: bool) -> PluginExecutionResult:
    """
    Export the current active context to a state file.

    Args:
        state_file_name (str): The name of the state file in which to export the current active context.
        overwrite (bool): A flag indicating that the state file should be overwritten, if it exists.

    Returns:
        state_file The persistent state file defining the current active context.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("export_state is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result
