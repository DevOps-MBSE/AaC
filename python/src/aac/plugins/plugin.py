"""Plugin metadata class."""

from typing import Optional
from attr import attrib, attrs, validators

from aac.plugins.contribution_points import ContributionPoints


@attrs(hash=False)
class Plugin:
    """
    A class that contains information relevant to AaC Plugins.

    Attributes:
        name: A string with the name of the plugin.
        contributions: A ContributionPoints object containing plugin contributions.
    """

    name: str = attrib(validator=validators.instance_of(str))
    contributions: Optional[ContributionPoints] = attrib(
        default=None, validator=validators.instance_of((ContributionPoints, type(None)))
    )

    def __hash__(self) -> int:
        """Return the hash for this Plugin object."""
        return hash(self.name)
