"""
A simple data class to collect AaC command info from plugins.
"""
from typing import Callable


class AacCommand:
    """
    A class used as a struct to hold a command name, command description, and callback.
    The command name is added to the argument parser with help set to teh command description.
    The callback is invoked if the user specifies the command.
    """

    def __init__(self, command_name: str, command_description: str, callback: Callable) -> None:
        self.command_name = command_name
        self.command_description = command_description
        self.callback = callback
