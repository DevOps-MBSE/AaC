"""A module for contribution point functionality."""

from enum import Enum
from typing import Callable, Union

from attr import Factory, attrib, attrs, validators

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.plugins.validators._validator_plugin import ValidatorPlugin


class ContributionPointNames(Enum):
    """The names of the contribution points that plugins can define."""

    COMMANDS = "commands"
    VALIDATIONS = "validations"
    DEFINITIONS = "definitions"


@attrs
class ContributionPoints:
    """
    A class to support contribution points which serve as hooks into AaC core for adding/customizing functionality.

    Attributes:
        contribution_points: The collection of contribution made by all plugins.
    """

    contribution_points: dict[ContributionPointNames, list] = attrib(
        default=Factory(dict), validator=validators.instance_of(dict)
    )

    def __attrs_post_init__(self):
        """Post-init hook for attrs classes."""
        [self.contribution_points.setdefault(value, []) for value in ContributionPointNames._member_map_.values()]

    def register_command(self, command: AacCommand) -> None:
        """Register the specified command."""
        self.register_commands([command])

    def register_commands(self, commands: list[AacCommand]) -> None:
        """Register the specified commands."""
        self._register_items(ContributionPointNames.COMMANDS, commands, lambda command: isinstance(command, AacCommand))

    def register_validation(self, validation: ValidatorPlugin) -> None:
        """Register the specified validation."""
        self.register_validations([validation])

    def register_validations(self, validations: list[ValidatorPlugin]) -> None:
        """Register the specified validations."""
        self._register_items(ContributionPointNames.VALIDATIONS, validations, lambda validation: isinstance(validation, ValidatorPlugin))

    def register_definition(self, definition: Definition) -> None:
        """Register the specified definition."""
        self.register_definitions([definition])

    def register_definitions(self, definitions: list[Definition]) -> None:
        """Register the specified definitions."""
        self._register_items(ContributionPointNames.DEFINITIONS, definitions, lambda definition: isinstance(definition, Definition))

    def _register_items(
        self,
        contribution_name: ContributionPointNames,
        items: Union[list[AacCommand], list[ValidatorPlugin], list[Definition]],
        validation: Callable
    ) -> None:
        """Register the specified items as contributions."""
        def register_item(item: Union[AacCommand, ValidatorPlugin, Definition]) -> None:
            if not validation(item):
                raise InvalidContributionPointError(f"Error adding {item.name} as a {contribution_name}")

            self.contribution_points[contribution_name].append(item)

        [register_item(item) for item in items]


@attrs
class InvalidContributionPointError(RuntimeError):
    """
    An error indicating an invalid contribution point.

    Attributes:
        message (str): An error message.
    """

    message: str = attrib(validator=validators.instance_of(str))
