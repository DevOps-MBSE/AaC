"""Module for loading data from the state file and making it available to the rest of the AaC package."""

import json

from aac import __version__
from aac.io.paths import sanitize_filesystem_path
from aac.lang.language_context import LanguageContext
from aac.persistence.state_file_error import StateFileError


def get_language_context_from_state_file(file_name: str) -> LanguageContext:
    """
    Return the language context loaded from the named state file.

    Args:
        file_name (str): The name of the state file.

    Returns:
        The language context after loading definitions from the files stored the state file.
    """
    language_context = LanguageContext()
    version, files, definitions, plugins = decode_state_file(file_name)

    if version != __version__:
        raise StateFileError(
            f"Version mismatch: State file written using version {version}; current AaC version {__version__}"
        )

    for file in files:
        uri = sanitize_filesystem_path(file)
        language_context.add_definitions_from_uri(uri, definitions)

    language_context.add_named_plugins(plugins)

    return language_context


def decode_state_file(file_name: str) -> tuple[str, list, list, list]:
    """
    Decode the state file and return the data.

    Args:
        file_name (str): The name of the state file.

    Returns:
        A tuple with (in order) the version, the files that contribute to the language context, the
        names of the definitions in the language context, and the names of the plugins in the
        language context.
    """
    with open(file_name) as state_file:
        object = json.loads(state_file.read()) or {}
        return (
            object.get("aac_version"),
            object.get("files"),
            object.get("definitions"),
            object.get("plugins"),
        )
