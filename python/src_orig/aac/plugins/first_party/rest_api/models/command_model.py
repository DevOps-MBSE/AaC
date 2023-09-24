"""Pydantic Version of the AaC command Class."""
from pydantic import BaseModel

from aac.execute.plugin_runner import AacCommand, AacCommandArgument


class CommandRequestModel(BaseModel):
    """Command model for user requests to execute commands."""
    name: str
    arguments: list[str]


class CommandResponseModel(BaseModel):
    """Response model for returning the results/outcomes of command requests."""
    command_name: str
    result_message: str
    success: bool


class CommandArgumentModel(BaseModel):
    """REST API Model for the AaC Command Argument class."""
    name: str
    description: str
    data_type: str
    optional: bool


class CommandModel(BaseModel):
    """REST API Model for the AaC Command class. Used to present available commands."""
    name: str
    description: str
    arguments: list[CommandArgumentModel]


def to_command_argument_model(command_argument: AacCommandArgument) -> CommandArgumentModel:
    """Return a CommandModel representation from an AacCommand object."""
    return CommandArgumentModel(
        name=command_argument.name, description=command_argument.description, data_type=command_argument.data_type, optional=command_argument.name.startswith("--")
    )


def to_command_model(command: AacCommand) -> CommandModel:
    """Return a CommandModel representation from an AacCommand object."""
    command_argument_models = list(map(to_command_argument_model, command.arguments))
    return CommandModel(
        name=command.name, description=command.description, arguments=command_argument_models
    )
