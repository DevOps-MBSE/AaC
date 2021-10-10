from typing import Callable


class AacCommand:

    def __init__(self, command_name: str, command_description: str, callback: Callable) -> None:
        self.command_name = command_name
        self.command_description = command_description
        self.callback = callback
