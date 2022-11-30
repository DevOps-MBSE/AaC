"""Plugin metadata class."""
from attr import Factory, attrib, attrs, validators

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_points import ContributionPoints
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution, PrimitiveValidationContribution


@attrs(hash=False, eq=False)
class Plugin:
    """
    A class that contains information relevant to AaC Plugins.

    Attributes:
        name: A string with the name of the plugin.
        contributions: A ContributionPoints object containing plugin contributions.
    """

    name: str = attrib(validator=validators.instance_of(str))
    contributions: ContributionPoints = attrib(
        init=False, default=Factory(ContributionPoints), validator=validators.instance_of(ContributionPoints)
    )

    def __hash__(self) -> int:
        """Return the hash for this Plugin object."""
        return hash(self.name)

    def __eq__(self, other):
        """Equality operator override."""
        return isinstance(other, Plugin) and self.name == other.name

    def register_commands(self, commands: list[AacCommand]):
        """Register the specified commands."""
        self.contributions.register_commands(self.name, commands)

    def get_commands(self) -> list[AacCommand]:
        """Get the commands registered by this plugin."""
        return self.contributions.get_commands_by_plugin_name(self.name)

    def register_definition_validations(self, validations: list[DefinitionValidationContribution]):
        """Register the specified validations."""
        self.contributions.register_definition_validations(self.name, validations)

    def get_definition_validations(self) -> list[DefinitionValidationContribution]:
        """Get the validations registered by this plugin."""
        return self.contributions.get_definition_validations_by_plugin_name(self.name)

    def register_primitive_validations(self, validations: list[PrimitiveValidationContribution]):
        """Register the specified primitive validations."""
        self.contributions.register_primitive_validations(self.name, validations)

    def get_primitive_validations(self) -> list[PrimitiveValidationContribution]:
        """Get the primitive validations registered by this plugin."""
        return self.contributions.get_primitive_validations_by_plugin_name(self.name)

    def register_definitions(self, definitions: list[Definition]):
        """Register the specified definitions."""
        self.contributions.register_definitions(self.name, definitions)

    def get_definitions(self) -> list[Definition]:
        """Get the definitions registered by this plugin."""
        return self.contributions.get_definitions_by_plugin_name(self.name)
