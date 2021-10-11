from aac import hookspec


@hookspec
def get_commands() -> list:
    '''
    Gets a list of AacCommand to register for use
    '''


@hookspec
def get_base_model_extensions() -> str:
    '''
    Gets data and ext definitions to apply to the AaC base.
    '''
