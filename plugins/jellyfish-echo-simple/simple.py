import jellyfish


@jellyfish.hookimpl
def echo(content: str):
    return content
