"""A module for contribution point functionality."""

from enum import Enum
from typing import Callable, Optional, Union

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

    def get_commands(self) -> list[AacCommand]:
        """Return the registered AacCommands."""
        return self._get_items(ContributionPointNames.COMMANDS)

    def get_command_by_name(self, name: str) -> Optional[AacCommand]:
        """Return the command with the specified name."""
        return self._get_item_by_name(ContributionPointNames.COMMANDS, name)

    def register_validation(self, validation: ValidatorPlugin) -> None:
        """Register the specified validation."""
        self.register_validations([validation])

    def register_validations(self, validations: list[ValidatorPlugin]) -> None:
        """Register the specified validations."""
        self._register_items(ContributionPointNames.VALIDATIONS, validations, lambda validation: isinstance(validation, ValidatorPlugin))

    def get_validations(self) -> list[AacCommand]:
        """Return the registered ValidatorPlugins."""
        return self._get_items(ContributionPointNames.VALIDATIONS)

    def get_validation_by_name(self, name: str) -> Optional[ValidatorPlugin]:
        """Return the validation with the specified name."""
        return self._get_item_by_name(ContributionPointNames.VALIDATIONS, name)

    def register_definition(self, definition: Definition) -> None:
        """Register the specified definition."""
        self.register_definitions([definition])

    def register_definitions(self, definitions: list[Definition]) -> None:
        """Register the specified definitions."""
        self._register_items(ContributionPointNames.DEFINITIONS, definitions, lambda definition: isinstance(definition, Definition))

    def get_definitions(self) -> list[AacCommand]:
        """Return the registered Definitions."""
        return self._get_items(ContributionPointNames.DEFINITIONS)

    def get_definition_by_name(self, name: str) -> Optional[Definition]:
        """Return the definition with the specified name."""
        return self._get_item_by_name(ContributionPointNames.DEFINITIONS, name)

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

    def _get_items(self, contribution_name: ContributionPointNames) -> list:
        return self.contribution_points.get(contribution_name, [])

    def _get_item_by_name(self, contribution_name: ContributionPointNames, name: str):
        items = [item for item in self._get_items(contribution_name) if item.name == name]
        return items[0] if len(items) > 0 else None


@attrs
class InvalidContributionPointError(RuntimeError):
    """
    An error indicating an invalid contribution point.

    Attributes:
        message (str): An error message.
    """

    message: str = attrib(validator=validators.instance_of(str))
