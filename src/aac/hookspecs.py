from aac import hookspec


@hookspec
def get_commands() -> list:
    '''
    Registers an AacCommand
    '''
