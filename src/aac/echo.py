# This python file is solely to provide a plugin example with the echo plugin until other, actual plugins are implemented.

from aac import plugin


def demonstrate_echo(content: str) -> None:
    print(f"Echoing {content}")
    results = plugin.get_plugin_manager().hook.echo(content=content)
    print(f"Plugin results: {results}")
