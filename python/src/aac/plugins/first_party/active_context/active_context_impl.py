"""AaC Plugin implementation module for the active-context plugin."""

from os.path import lexists

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "active-context"


def list_files() -> PluginExecutionResult:
    """
    Display the files in the active context.

    Returns:
        files Files that are in the active context.
    """

    def collect_files() -> str:
        file_uris = [file.uri for file in get_active_context().get_files_in_context()]
        file_uris.sort(reverse=True)  # Perform an alphabetical sort

        return "\n".join(file_uris)

    with plugin_result(plugin_name, collect_files) as result:
        return result


def list_definitions() -> PluginExecutionResult:
    """
    List all definitions within the active context.

    Returns:
        definitions The list of all definitions that are in the active context.
    """

    def get_definitions_in_active_context() -> str:
        return "\n".join(get_active_context().get_defined_types())

    with plugin_result(plugin_name, get_definitions_in_active_context) as result:
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

    def get_definition_info() -> str:
        definition = get_active_context().get_definition_by_name(definition_name)
        if definition is None:
            raise PluginError(f"{definition_name} is not in the active context.")

        return f"{definition.source.uri}:{definition.lexemes[0].location.line + 1}\n\n{definition.to_yaml()}"

    with plugin_result(plugin_name, get_definition_info) as result:
        return result


def import_state(state_file: str) -> PluginExecutionResult:
    """
    Configure the active context to be initialized with the definitions, plugins, etc from a state file.

    Args:
        state_file (str): The persistent state file from which to get information about how to configure the active context.
    """

    def import_state_file_if_present() -> str:
        if not lexists(state_file):
            raise PluginError(f"The state file {state_file} could not be imported because it doesn't exist.")

        active_context = get_active_context()
        active_context.import_from_file(state_file)
        return f"Successfully imported active context from {state_file}"

    with plugin_result(plugin_name, import_state_file_if_present) as result:
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

    def export_active_context_to_state_file():
        if lexists(state_file_name) and not overwrite:
            raise PluginError(f"The file {state_file_name} already exists and overwrite not specified.")

        get_active_context().export_to_file(state_file_name)
        return f"Successfully exported active context to {state_file_name}."

    with plugin_result(plugin_name, export_active_context_to_state_file) as result:
        return result
