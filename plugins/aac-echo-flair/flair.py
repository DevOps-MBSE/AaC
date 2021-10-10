import aac


@aac.hookimpl
def echo(content: str):
    return f"~~ {content} ~~"
