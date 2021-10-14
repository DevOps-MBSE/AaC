"""
Defines the AaC plugin interface
"""
from aac import hookspec
from aac.AacCommand import AacCommand


@hookspec
def get_commands() -> list[AacCommand]:
    '''
    Gets a list of AacCommand to register for use
    '''


@hookspec
def get_base_model_extensions() -> str:
    '''
    Gets data and ext definitions to apply to the AaC base.
    '''
