"""Plugin metadata class."""
from attr import Factory, attrib, attrs, validators

from aac.cli.aac_command import AacCommand
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_points import ContributionPoints
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution, PrimitiveValidationContribution


@attrs(hash=False, eq=False)
class Plugin:
    """
    Provides a consistent data model for AaC Plugins, and it exposes the plugins' contribution points which are used to add features and functionality to the AaC plugins.

    Plugins must be told what content they have/provide such as definitions (schemas, extensions, etc),
    AaC commands (validate, gen-plugin, etc), or validation (definitions, primitives). If the content isn't
    registered to the plugin model then it will not show up when AaC commands are run or when definitions are validated.

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
        """
        Registers plugin commands that can then be executed.

        Args:
            commands (list[AacCommand]): A list of AacCommand data structures that describe
                the name, function, and corresponding arguments for plugin-provided AaC commands.
        """
        self.contributions.register_commands(self.name, commands)

    def get_commands(self) -> list[AacCommand]:
        """Get the commands provided by this plugin."""
        return self.contributions.get_commands_by_plugin_name(self.name)

    def register_definition_validations(self, validations: list[DefinitionValidationContribution]):
        """
        Registers definition validations that can then be used in the validation of structural constraints.

        Args:
            validations (list[DefinitionValidationContribution]): A list of DefinitionValidationContribution
                data structures that describe the name, function, and corresponding validation definition for
                each validation.
        """
        self.contributions.register_definition_validations(self.name, validations)

    def get_definition_validations(self) -> list[DefinitionValidationContribution]:
        """Get the validations provided by this plugin."""
        return self.contributions.get_definition_validations_by_plugin_name(self.name)

    def register_primitive_validations(self, validations: list[PrimitiveValidationContribution]):
        """
        Registers primitive validations that can then be used in the validation of primitive type constraints.

        Args:
            validations (list[PrimitiveValidationContribution]): A list of DefinitionValidationContribution
                data structures that describe the name, function, and corresponding primitive type for
                each validation.
        """
        self.contributions.register_primitive_validations(self.name, validations)

    def get_primitive_validations(self) -> list[PrimitiveValidationContribution]:
        """Get the primitive validations provided by this plugin."""
        return self.contributions.get_primitive_validations_by_plugin_name(self.name)

    def register_definitions(self, definitions: list[Definition]):
        """
        Registers definitions for the plugin to provide. Definitions here will be added to the context when the plugin is active.

        Args:
            definitions (list[Definition]): A list of Definition data structures that are provided
                by the definition.
        """
        self.contributions.register_definitions(self.name, definitions)

    def get_definitions(self) -> list[Definition]:
        """Get the definitions provided by this plugin."""
        return self.contributions.get_definitions_by_plugin_name(self.name)
