"""AaC Module for easy file writing."""
import sys
import logging
from os import path, makedirs

from aac.context.definition import Definition
from aac.in_out.constants import DEFINITION_SEPARATOR
from aac.in_out.paths import sanitize_filesystem_path


def write_file(uri: str, content: str, overwrite: bool = False) -> None:
    """
    Write string content to a file.

    Args:
        uri (str): the file's full uri
        content (str): contents of the file to write
        overwrite (bool): True to overwrite an existing file or false to not.
    """
    sanitized_uri = sanitize_filesystem_path(uri)
    does_file_exist = path.exists(sanitized_uri)
    file_parent_dir = path.dirname(sanitized_uri)

    if not path.exists(file_parent_dir):
        makedirs(file_parent_dir, exist_ok=True)

    if not overwrite and does_file_exist:
        logging.info(f"{sanitized_uri} already exists, skipping write.")
        return

    try:
        with open(sanitized_uri, "w") as file:
            file.writelines(content)
    except IOError as error:
        logging.error(f"Failed to write file {sanitized_uri} due to error: {error}")


def write_definitions_to_file(definitions: list[Definition], file_uri: str, is_user_editable: bool = True) -> None:
    """
    Given a list of definitions, write them to file uri. Updates the source for definitions passed in.

    Args:
        definitions (list[Definition]): The definitions to write to file.
        file_uri (str): The URI of the file to write the definitions to.
        is_user_editable (bool): True if the AaC file can be edited by users.
    """
    def sort_definitions_by_lexeme_line(definition: Definition) -> int:
        line = sys.maxsize

        if definition.lexemes and definition.lexemes[0].source == file_uri:
            line = definition.lexemes[0].location.line

        return line

    definitions.sort(key=sort_definitions_by_lexeme_line)

    file_content = ""
    for definition in definitions:
        definition.source.uri = file_uri
        definition.source.is_user_editable = is_user_editable

        yaml_doc_separator = DEFINITION_SEPARATOR if file_content else ""
        file_content += f"{yaml_doc_separator}{definition.to_yaml()}"

    write_file(file_uri, file_content, True)
