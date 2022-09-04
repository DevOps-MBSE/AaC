"""A temporary test text document."""

from contextlib import contextmanager
from typing import Generator
from os import path

from aac.lang.definitions.definition import Definition
from attr import attrib, attrs
from attr.validators import instance_of


@attrs(slots=True)
class TextDocument:
    """
    A temporary text document used by the LSP testing framework.

    Attributes:
        file_path (str): The file path to the temporary text document.
        file_name (str): The name of the temporary text document.
        content (str): The content of the temporary text document.
        version (int): The version of the content of the temporary text document. Every time the content changes, the version
                           number would be incremented.
    """

    file_path: str = attrib(validator=instance_of(str))
    file_name: str = attrib(validator=instance_of(str))
    content: str = attrib(validator=instance_of(str))
    version: int = attrib(default=0, validator=instance_of(int), init=False)

    def __attrs_post_init__(self):
        """Post init method. Called by attrs constructor."""
        self.write(self.content)

    def read(self) -> str:
        """Return the contents of the temporary text document."""
        return self.content

    def write(self, content: str) -> None:
        """
        Write the updated contents to the temporary text document.

        Args:
            content (str): The contents to be written to the temporary text document.
        """
        self.content = content
        with open(path.join(self.file_path, self.file_name), "w") as file:
            file.write(content)

    def write_definitions(self, *definitions: Definition) -> None:
        """
        Write the definitions to the temporary text document.

        Args:
            definitions (list[Definition]): The list of definitions to be written to the temporary text document.
        """
        yaml_definitions = [definition.to_yaml() for definition in definitions]
        self.write("---".join(yaml_definitions))


@contextmanager
def text_document(file_path: str, file_name: str, content: str) -> Generator[TextDocument, None, None]:
    """
    Provide a temporary text document.

    Args:
        file_path (str): The file path to the temporary text document.
        file_name (str): The name of the temporary text document.
        content (str): The content of the temporary text document.

    Yields:
        The temporary text document.
    """
    yield TextDocument(file_path, file_name, content)
