"""A contribution that can be made by a plugin."""

from attr import Factory, attrib, attrs, validators

from aac.plugins.contributions.contribution_types import ContributionType


@attrs(hash=False)
class PluginContribution:
    """
    A contribution made by a plugin.

    Attributes:
        plugin_name: The name of the plugin that contributes the specified item(s).
        contribution_type: The type of contributions being made by the plugin.
        items: The items being contributed by the plugin.
    """

    plugin_name: str = attrib(validator=validators.instance_of(str))
    contribution_type: ContributionType = attrib(validator=validators.instance_of(ContributionType))
    items: set = attrib(default=Factory(set), validator=validators.instance_of(set))

    def is_contribution_type(self, contribution_type: ContributionType) -> bool:
        """Return whether the contribution is of the specified contribution type."""
        return self.contribution_type == contribution_type

    def __hash__(self) -> int:
        """Return a hash of the current object."""
        return hash(f"{self.plugin_name}:{self.contribution_type}")
