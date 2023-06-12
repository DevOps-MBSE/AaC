"""A module for contribution point functionality."""

from typing import Any, Callable, Optional, Union

from attr import Factory, attrib, attrs, validators

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_types import ContributionType, DefinitionValidationContribution, PrimitiveValidationContribution
from aac.plugins.contributions.plugin_contribution import PluginContribution


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

    # Definition Validation Contribution Point

    def register_definition_validation(self, plugin_name: str, validation: DefinitionValidationContribution) -> None:
        """
        Register the specified definition validation.

        The definition validation contribution point is used to register programmatic
            implementations of definition validation rules.

        Args:
            plugin_name (str): The name of the plugin that is providing the definition validation.
            validation (DefinitionValidationContribution): The definition validation that are being registered.
        """
        self.register_definition_validations(plugin_name, [validation])

    def register_definition_validations(self, plugin_name: str, validations: list[DefinitionValidationContribution]) -> None:
        """
        Register the specified definition validations.

        The definition validation contribution point is used to register programmatic
            implementations of definition validation rules.

        Args:
            plugin_name (str): The name of the plugin that is providing the definition validation.
            validations (list[DefinitionValidationContribution]): The definition validations that are being registered.
        """

        def validate(validation: Any) -> bool:
            return isinstance(validation, DefinitionValidationContribution)

        self._register_contributions(plugin_name, ContributionType.DEFINITION_VALIDATIONS, validations, validate)

    def get_definition_validations(self) -> list[DefinitionValidationContribution]:
        """Return the registered DefinitionValidationContribution."""
        return self._get_items(ContributionType.DEFINITION_VALIDATIONS)

    def get_definition_validation_by_name(self, name: str) -> Optional[DefinitionValidationContribution]:
        """Return the definition validation with the specified name."""
        return self._get_item_by_name(ContributionType.DEFINITION_VALIDATIONS, name)

    def get_definition_validations_by_plugin_name(self, plugin_name: str) -> list[DefinitionValidationContribution]:
        """Return the definition validation with the specified name."""
        return self._get_items_by_plugin_name(ContributionType.DEFINITION_VALIDATIONS, plugin_name)

    # Primitive Validation Contribution Point

    def register_primitive_validation(self, plugin_name: str, validation: PrimitiveValidationContribution) -> None:
        """Register the specified primitive type validation.

        The primitive validation contribution point is used to register programmatic
            implementations of primitive validation rules.

        Args:
            plugin_name (str): The name of the plugin that is providing the primitive validation.
            validation (PrimitiveValidationContribution): The definition validation that are being registered.
        """
        self.register_definition_validations(plugin_name, [validation])

    def register_primitive_validations(self, plugin_name: str, validations: list[PrimitiveValidationContribution]) -> None:
        """
        Register the specified primitive type validations.

        The primitive validation contribution point is used to register programmatic
            implementations of primitive validation rules.

        Args:
            plugin_name (str): The name of the plugin that is providing the primitive validation.
            validations (list[PrimitiveValidationContribution]): The definition validations that are being registered.
        """

        def validate(validation: Any) -> bool:
            return isinstance(validation, PrimitiveValidationContribution)

        self._register_contributions(plugin_name, ContributionType.PRIMITIVE_VALIDATIONs, validations, validate)

    def get_primitive_validations(self) -> list[AacCommand]:
        """Return the primitive validations Definitions."""
        return self._get_items(ContributionType.PRIMITIVE_VALIDATIONs)

    def get_primitive_validations_by_name(self, name: str) -> Optional[Definition]:
        """Return the primitive validations with the specified name."""
        return self._get_item_by_name(ContributionType.PRIMITIVE_VALIDATIONs, name)

    def get_primitive_validations_by_plugin_name(self, plugin_name: str) -> list[Definition]:
        """Return the primitive validations with the specified name."""
        return self._get_items_by_plugin_name(ContributionType.PRIMITIVE_VALIDATIONs, plugin_name)

    # Helper Functions

    def _register_contributions(
        self,
        plugin_name: str,
        contribution_name: ContributionType,
        items: list[Union[AacCommand, DefinitionValidationContribution, PrimitiveValidationContribution, Definition]],
        validation: Callable,
    ) -> None:
        def register_contribution(item) -> None:
            if not validation(item):
                raise InvalidContributionPointError(
                    f"Error adding {item.name} as a {contribution_name} registered by {plugin_name}"
                )

            contribution_items.add(item)

        contribution_items = set()

        for item in items:
            register_contribution(item)

        self.contributions.add(PluginContribution(plugin_name, contribution_name, contribution_items))

    def _get_contributions_by_type(self, contribution_type: ContributionType) -> list[PluginContribution]:
        return [contrib for contrib in self.contributions if contrib.is_contribution_type(contribution_type)]

    def _get_items(self, contribution_type: ContributionType) -> list:
        contribution_lists = [contrib.items for contrib in self._get_contributions_by_type(contribution_type)]
        return [contribution for contribution_list in contribution_lists for contribution in contribution_list]

    def _get_item_by_name(self, contribution_type: ContributionType, name: str):
        items = [item for item in self._get_items(contribution_type) if item.name == name]
        return items[0] if len(items) > 0 else None

    def _get_items_by_plugin_name(self, contribution_type: ContributionType, plugin_name: str) -> list:
        contributions = [
            contrib for contrib in self._get_contributions_by_type(contribution_type) if contrib.plugin_name == plugin_name
        ]
        return list(contributions[0].items) if len(contributions) > 0 else []


@attrs
class InvalidContributionPointError(RuntimeError):
    """
    An error indicating an invalid contribution point.

    Attributes:
        message (str): An error message.
    """

    message: str = attrib(validator=validators.instance_of(str))
