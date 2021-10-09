import jellyfish


@jellyfish.hookimpl
def echo(content: str):
    return f"~~ {content} ~~"
