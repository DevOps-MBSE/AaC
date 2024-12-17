"""An exception class representing a language error condition."""
from attr import attrib, attrs, validators


@attrs(slots=True)
class LanguageError(Exception):
    """A base class representing a language error."""
    message: str = attrib(validator=validators.instance_of(str))
    location: str = attrib(validator=validators.instance_of(str))

    def __init__(self, message: str, location: str):
        """
        An init constructor for the Language Error Class.

        Args:
            message (str): The error message.
            location (str): The source location of the error.
        """
        self.message = message
        self.location = location

    def __str__(self) -> str:
        """
        Method for defining how Language Error looks when represented as a string.

        Returns:
            The Language Error represented as a string.
        """
        return f"Error: {self.message}. Location: {self.location}"
