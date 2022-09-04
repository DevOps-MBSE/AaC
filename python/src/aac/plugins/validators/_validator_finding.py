"""
A module for defining a validator finding.

Validator findings are created when a validator plugin wants to provide feedback to a user about a
definition. Validation errors are a subset of the category of validator findings but findings need
not be limited to errors, so this module also exports a severity that informs how severe the finding
is.
"""

from enum import Enum, auto
from aac.io.files.aac_file import AaCFile
from aac.lang.definitions.source_location import SourceLocation

from attr import attrib, attrs, validators

from aac.lang.definitions.definition import Definition


class FindingSeverity(Enum):
    """A severity for distinguishing between different kinds of validator findings."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@attrs(slots=True)
class FindingLocation:
    """
    A representation of the location of a validator finding.

    Attributes:
        validation_name (str): The name of the validator plugin that made the finding.
        source_file (AaCFile): The file in which the finding occurred.
        location (SourceLocation): The source location of the finding.
    """

    validation_name: str = attrib(validator=validators.instance_of(str))
    source_file: AaCFile = attrib(validator=validators.instance_of(AaCFile))
    location: SourceLocation = attrib(validator=validators.instance_of(SourceLocation))


@attrs(slots=True)
class ValidatorFinding:
    """
    A finding made in a validator plugin.

    Attributes:
        definition (Definition): The definition on which the finding was made.
        severity (FindingSeverity): The severity of the finding.
        message (str): A message for the user to know how to address the finding, if needed.
        location (FindingLocation): An object containing information about the location of the
                                    finding.
    """

    definition: Definition = attrib(validator=validators.instance_of(Definition))
    severity: FindingSeverity = attrib(validator=validators.instance_of(FindingSeverity))
    message: str = attrib(validator=validators.instance_of(str))
    location: (FindingLocation) = attrib(validator=validators.instance_of(FindingLocation))
