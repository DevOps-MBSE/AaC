from aac import hookspec


@hookspec
def echo(content: str) -> str:
    """Echo the incoming string.

    :param content: the content to repeat back
    :return: the content that's repeated back
    """
