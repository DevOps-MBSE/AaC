"""A module for contribution point functionality."""

from typing import Any, Callable, Optional, Union
from iteration_utilities import flatten

from attr import Factory, attrib, attrs, validators

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_type import ContributionType
from aac.plugins.contributions.plugin_contribution import PluginContribution
from aac.plugins.validators._validator_plugin import ValidatorPlugin


@attrs
class ContributionPoints:
    """
    A class to support contribution points which serve as hooks into AaC core for adding/customizing functionality.

    See ContributionType for the complete list of contribution types.

    Attributes:
        contributions: The collection of contribution made by all plugins.
    """

    contributions: set[PluginContribution] = attrib(default=Factory(set), validator=validators.instance_of(set))

    # AaC Command Contribution Point

    def register_command(self, plugin_name: str, command: AacCommand) -> None:
        """Register the specified command."""
        self.register_commands(plugin_name, [command])

    def register_commands(self, plugin_name: str, commands: list[AacCommand]) -> None:
        """Register the specified commands."""

        def validate(command: Any) -> bool:
            return isinstance(command, AacCommand)

        self._register_contributions(plugin_name, ContributionType.COMMANDS, commands, validate)

    def get_commands(self) -> list[AacCommand]:
        """Return the registered AacCommands."""
        return self._get_items(ContributionType.COMMANDS)

    def get_command_by_name(self, name: str) -> Optional[AacCommand]:
        """Return the command with the specified name."""
        return self._get_item_by_name(ContributionType.COMMANDS, name)

    def get_commands_by_plugin_name(self, plugin_name: str) -> list[AacCommand]:
        """Return the command with the specified name."""
        return self._get_items_by_plugin_name(ContributionType.COMMANDS, plugin_name)

    # Validator Contribution Point

    def register_validation(self, plugin_name: str, validation: ValidatorPlugin) -> None:
        """Register the specified validation."""
        self.register_validations(plugin_name, [validation])

    def register_validations(self, plugin_name: str, validations: list[ValidatorPlugin]) -> None:
        """Register the specified validations."""

        def validate(validation: Any) -> bool:
            return isinstance(validation, ValidatorPlugin)

        self._register_contributions(plugin_name, ContributionType.VALIDATIONS, validations, validate)

    def get_validations(self) -> list[ValidatorPlugin]:
        """Return the registered ValidatorPlugins."""
        return self._get_items(ContributionType.VALIDATIONS)

    def get_validation_by_name(self, name: str) -> Optional[ValidatorPlugin]:
        """Return the validation with the specified name."""
        return self._get_item_by_name(ContributionType.VALIDATIONS, name)

    def get_validations_by_plugin_name(self, plugin_name: str) -> list[ValidatorPlugin]:
        """Return the validation with the specified name."""
        return self._get_items_by_plugin_name(ContributionType.VALIDATIONS, plugin_name)

    # Definition Contribution Point

    def register_definition(self, plugin_name: str, definition: Definition) -> None:
        """Register the specified definition."""
        self.register_definitions(plugin_name, [definition])

    def register_definitions(self, plugin_name: str, definitions: list[Definition]) -> None:
        """Register the specified definitions."""

        def validate(definition: Any) -> bool:
            return isinstance(definition, Definition)

        self._register_contributions(plugin_name, ContributionType.DEFINITIONS, definitions, validate)

    def get_definitions(self) -> list[AacCommand]:
        """Return the registered Definitions."""
        return self._get_items(ContributionType.DEFINITIONS)

    def get_definition_by_name(self, name: str) -> Optional[Definition]:
        """Return the definition with the specified name."""
        return self._get_item_by_name(ContributionType.DEFINITIONS, name)

    def get_definitions_by_plugin_name(self, plugin_name: str) -> list[Definition]:
        """Return the definition with the specified name."""
        return self._get_items_by_plugin_name(ContributionType.DEFINITIONS, plugin_name)

    # Primitive Type Validation Point

    def register_primitive_validation(self, plugin_name: str, validation: ValidatorPlugin) -> None:
        """Register the specified primitives validation."""
        self.register_validations(plugin_name, [validation])

    def register_primitive_validations(self, plugin_name: str, validations: list[ValidatorPlugin]) -> None:
        """Register the specified primitives validations."""

        def validate(validation: Any) -> bool:
            return isinstance(validation, ValidatorPlugin)

        self._register_contributions(plugin_name, ContributionType.PRIMITIVE_VALIDATION, validations, validate)

    def get_primitive_validations(self) -> list[AacCommand]:
        """Return the primitive validations Definitions."""
        return self._get_items(ContributionType.PRIMITIVE_VALIDATION)

    def get_primitive_validations_by_name(self, name: str) -> Optional[Definition]:
        """Return the primitive validations with the specified name."""
        return self._get_item_by_name(ContributionType.PRIMITIVE_VALIDATION, name)

    def get_primitive_validations_by_plugin_name(self, plugin_name: str) -> list[Definition]:
        """Return the primitive validations with the specified name."""
        return self._get_items_by_plugin_name(ContributionType.PRIMITIVE_VALIDATION, plugin_name)

    # Helper Functions

    def _register_contributions(
        self,
        plugin_name: str,
        contribution_name: ContributionType,
        items: Union[list[AacCommand], list[ValidatorPlugin], list[Definition]],
        validation: Callable
    ) -> None:

        def register_contribution(item) -> None:
            if not validation(item):
                raise InvalidContributionPointError(f"Error adding {item.name} as a {contribution_name} registered by {plugin_name}")

            contribution_items.add(item)

        contribution_items = set()

        for item in items:
            register_contribution(item)

        self.contributions.add(PluginContribution(plugin_name, contribution_name, contribution_items))

    def _get_contributions_by_type(self, contribution_type: ContributionType) -> list[PluginContribution]:
        return [contrib for contrib in self.contributions if contrib.is_contribution_type(contribution_type)]

    def _get_items(self, contribution_type: ContributionType) -> list:
        return list(flatten([contrib.items for contrib in self._get_contributions_by_type(contribution_type)]))

    def _get_item_by_name(self, contribution_type: ContributionType, name: str):
        items = [item for item in self._get_items(contribution_type) if item.name == name]
        return items[0] if len(items) > 0 else None

    def _get_items_by_plugin_name(self, contribution_type: ContributionType, plugin_name: str) -> list:
        contributions = [contrib for contrib in self._get_contributions_by_type(contribution_type) if contrib.plugin_name == plugin_name]
        return list(contributions[0].items) if len(contributions) > 0 else []


@attrs
class InvalidContributionPointError(RuntimeError):
    """
    An error indicating an invalid contribution point.

    Attributes:
        message (str): An error message.
    """

    message: str = attrib(validator=validators.instance_of(str))
