"""Validation plugin to ensure that each validation definition has a corresponding validation function."""

from aac.AacCommand import AacCommand
from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.validation.Validator_Plugin import Validator_Plugin


@hookimpl
def register_validators() -> Validator_Plugin:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and data definitions employed by the plugin
    """
    return Validator_Plugin.from_definition({})


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    This function is automatically generated. Do not edit.

    Returns:
        list of AacCommands
    """
    return []


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Returns the CommandBehaviorType modeling language extension to the plugin infrastructure.

    Returns:
        string representing yaml extensions and data definitions employed by the plugin
    """
    return get_resource_file_contents(__package__, "gen_design_doc.yaml")
