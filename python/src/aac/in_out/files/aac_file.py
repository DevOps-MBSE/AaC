"""File metadata and management class for AaC."""
from attr import attrib, attrs, validators


@attrs(hash=False, eq=False)
class AaCFile:
    """
    An Architecture-as-Code file containing AaC definitions.

    Attributes:
        uri (str): The file's URI path
        is_user_editable (bool): True if the file can be edited by the user, otherwise false
        is_loaded_in_context (bool): True if the file is currently loaded into the context, otherwise false
    """
    uri: str = attrib(validator=validators.instance_of(str))
    is_user_editable: bool = attrib(validator=validators.instance_of(bool))
    is_loaded_in_context: bool = attrib(validator=validators.instance_of(bool))

    def __hash__(self):
        """Hash function for the class."""
        return hash(self.uri)

    def __eq__(self, obj):
        """Equals function for the class."""
        return isinstance(obj, AaCFile) and obj.uri == self.uri
