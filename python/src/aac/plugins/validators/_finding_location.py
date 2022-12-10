"""A module for defining a finding location."""
from aac.io.files.aac_file import AaCFile
from aac.lang.definitions.source_location import SourceLocation

from attr import attrib, attrs, validators


@attrs(init=False, slots=True)
class FindingLocation:
    """
    A representation of the location of a validator finding.

    Attributes:
        validation_name (str): The name of the validator plugin that made the finding.
        source_uri (AaCFile): The file in which the finding occurred.
        location (SourceLocation): The source location of the finding.
    """

    validation_name: str = attrib(validator=validators.instance_of(str))
    source: AaCFile = attrib(validator=validators.instance_of(AaCFile))
    location: SourceLocation = attrib(validator=validators.instance_of(SourceLocation))

    def __init__(
        self,
        validation_name: str,
        source_uri: AaCFile,
        line: int,
        column: int,
        position: int,
        span: int,
    ) -> None:
        """Initialize a new FindingLocation object."""
        self.validation_name = validation_name
        self.source = source_uri
        self.location = SourceLocation(line, column, position, span)
