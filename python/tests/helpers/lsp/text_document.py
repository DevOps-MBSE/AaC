"""A virtual text document."""

from contextlib import contextmanager
from typing import Generator

from aac.lang.definitions.definition import Definition
from attr import attrib, attrs
from attr.validators import instance_of


@attrs(slots=True)
class TextDocument:
    """
    A virtual text document used by the LSP testing framework.

    Attributes:
        file_name (str): The name of the virtual text document.
        content (str): The content of the virtual text document.
        version (int): The version of the content of the virtual text document. Every time the content changes, the version
                           number would be incremented.
    """

    file_name: str = attrib(validator=instance_of(str))
    content: str = attrib(validator=instance_of(str))
    version: int = attrib(default=0, validator=instance_of(int), init=False)

    def read(self) -> str:
        """Return the contents of the virtual text document."""
        return self.content

    def write(self, content: str) -> None:
        """
        Write the updated contents to the virtual text document.

        Args:
            content (str): The contents to be written to the virtual text document.
        """
        self.content = content

    def write_definitions(self, *definitions: Definition) -> None:
        """
        Write the definitions to the virtual text document.

        Args:
            definitions (list[Definition]): The list of definitions to be written to the virtual text document.
        """
        yaml_definitions = [definition.to_yaml() for definition in definitions]
        self.write("---".join(yaml_definitions))


@contextmanager
def text_document(file_name: str, content: str) -> Generator[TextDocument, None, None]:
    """
    Provide a virtual text document.

    Args:
        file_name (str): The name of the virtual text document.
        content (str): The content of the virtual text document.

    Yields:
        The virtual text document.
    """
    yield TextDocument(file_name, content)
