import jellyfish


@jellyfish._plugin.hookimpl
def echo(content: str):
    return f"~~ {content} ~~"
