from typing import Callable, Optional

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.plugins.plugin import Plugin, DefinitionValidationContribution, PrimitiveValidationContribution


def create_plugin(
    name: str,
    definitions: Optional[list[Definition]] = None,
    commands: Optional[list[AacCommand]] = None,
    definition_validations: Optional[list[DefinitionValidationContribution]] = None,
    primitive_validations: Optional[list[PrimitiveValidationContribution]] = None,
) -> Plugin:
    plugin = Plugin(name)

    if definitions:
        plugin.register_definitions(definitions)

    if commands:
        plugin.register_commands(commands)

    if definition_validations:
        plugin.register_definition_validations(definition_validations)

    if primitive_validations:
        plugin.register_primitive_validations(primitive_validations)

    return plugin


def check_generated_file_contents(path: str, checker: Callable, *args, **kwargs):
    """Check the contents of the provided file at path according to checker.

    Args:
        path (str): The file path whose contents will be checked.
        checker (Callable): A function that checks the file contents appropriately. The first
                            argument will be the file contents.
        *args: Any extra arguments to pass to the checker.
        **kwargs: Any extra keyword arguments to pass to the checker.

    Returns:
        If checker returns anything, return that. Otherwise, returns None.
    """
    with open(path) as generated_file:
        return checker(generated_file.read(), *args, **kwargs)
