"""
Parse Architecture-as-Code YAML files.

The AaC parser reads a YAML file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""

import logging

from copy import deepcopy
from os import path, linesep
from typing import Optional
from yaml import Mark, Token, StreamStartToken, StreamEndToken, DocumentStartToken

from aac.io.constants import DEFAULT_SOURCE_URI
from aac.io.files.aac_file import AaCFile
from aac.io.parser._cache_manager import get_cache
from aac.io.paths import sanitize_filesystem_path
from aac.lang.constants import DEFINITION_FIELD_FILES, DEFINITION_FIELD_NAME, ROOT_KEY_IMPORT
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation


YAML_CACHE = get_cache()


def parse(source: str, source_uri: Optional[str] = None) -> list[Definition]:
    """
    Parse the Architecture-as-Code (AaC) definition(s) from the provided source.

    Args:
        source (str): Must be either a file path to an AaC yaml file or a string containing AaC definitions.
        source_uri (Optional[str]): Overrides and sets the source_uri

    Returns:
        A list of Definition objects containing the internal representation of the definition and metadata
        associated with the definition.
    """
    # Linesep provides a quick and cheap filter for filepaths. A valid filepath won't have newlines.
    sanitized_source = source
    is_file = False

    if linesep not in source:
        sanitized_source = sanitize_filesystem_path(source)
        if path.lexists(sanitized_source):
            is_file = True

    return _parse_file(sanitized_source) if is_file else _parse_str(source_uri or DEFAULT_SOURCE_URI, source)


def _parse_file(arch_file: str) -> list[Definition]:
    """
    Parse an Architecture-as-Code YAML file and return the definitions in it.

    Args:
        arch_file (str): The Architecture-as-Code YAML file to be parsed.

    Returns:
        The AaC definitions extracted from the specified file.
    """
    definition_lists = [_parse_str(file, _read_file_content(file)) for file in _get_files_to_process(arch_file)]
    return [definition for definition_list in definition_lists for definition in definition_list]


def _parse_str(source: str, model_content: str) -> list[Definition]:
    """
    Parse a string containing one or more YAML model definitions.

    Args:
        source:  The file the content came from (to help with better logging)
        model_content:  The YAML to parse

    Returns:
        The AaC definitions that were built from the model contents.
    """

    def mark_to_source_location(start: Mark, end: Mark) -> SourceLocation:
        return SourceLocation(start.line, start.column, start.index, end.column - start.column)

    def get_lexemes_for_definition(value_tokens, content_start, content_end) -> list[Lexeme]:
        definition_tokens = [token for token in value_tokens if is_token_between_locations(token, content_start, content_end)]
        definition_lexemes = []
        for token in definition_tokens:
            location = mark_to_source_location(token.start_mark, token.end_mark)
            definition_lexemes.append(Lexeme(location, source, token.value))
        return definition_lexemes

    def is_token_between_locations(token, inclusive_line_start: int, inclusive_line_end: int) -> list[Lexeme]:
        return token.start_mark.line >= inclusive_line_start and token.end_mark.line <= inclusive_line_end

    yaml_tokens: list[Token] = YAML_CACHE.scan_string(model_content)
    value_tokens: list[Token] = [token for token in yaml_tokens if hasattr(token, "value")]
    doc_start_token: list[StreamStartToken] = [token for token in yaml_tokens if isinstance(token, StreamStartToken)]
    doc_end_token: list[StreamEndToken] = [token for token in yaml_tokens if isinstance(token, StreamEndToken)]
    doc_segment_tokens: list[DocumentStartToken] = [token for token in yaml_tokens if isinstance(token, DocumentStartToken)]
    doc_tokens = [*doc_start_token, *doc_segment_tokens, *doc_end_token]

    yaml_dicts: list[dict] = deepcopy(YAML_CACHE.parse_string(model_content))

    source_files: dict[str, AaCFile] = {}
    definitions: list[Definition] = []
    for doc_token_index in range(0, len(doc_tokens) - 1):
        start_doc_token = doc_tokens[doc_token_index]
        end_doc_token = doc_tokens[doc_token_index + 1]

        content_start_line = start_doc_token.start_mark.line
        content_end_line = end_doc_token.end_mark.line + (1 if isinstance(end_doc_token, StreamEndToken) else 0)

        yaml_text = linesep.join(model_content.splitlines()[content_start_line:content_end_line])
        yaml_text += linesep

        if yaml_text.strip():
            definition_lexemes = get_lexemes_for_definition(value_tokens, content_start_line, content_end_line)

            if yaml_dicts:
                source_file = source_files.get(source)
                if not source_file:
                    source_file = AaCFile(source, True, False)
                    source_files[source] = source_file

                root_yaml = yaml_dicts.pop(0)
                root_type, *_ = root_yaml.keys()
                definition_name = root_yaml.get(root_type, {}).get(DEFINITION_FIELD_NAME, "")

                new_definition = Definition(
                    name=definition_name,
                    content=yaml_text,
                    source=source_file,
                    meta_structure=None,
                    lexemes=definition_lexemes,
                    structure=root_yaml,
                )
                definitions.append(new_definition)
        else:
            logging.info(
                f"Skipping empty content between {start_doc_token}:L{content_start_line} and {end_doc_token}:L{content_end_line} in source {source}"
            )
            logging.debug(f"Source: {source} Content:{model_content}")
            logging.debug(f"Content lines:{model_content.splitlines()}")

    return definitions


def _read_file_content(arch_file: str) -> str:
    """
    Read file content method extracts text content from the specified file.

    Args:
        arch_file: The file to read.

    Returns:
        The contents of the file as a string.
    """
    with open(arch_file, "r") as file:
        return file.read()


def _get_files_to_process(arch_file_path: str) -> list[str]:
    """
    Return a list of all files referenced in the model.

    Traverse the import path starting from the specified file and return a list of all files referenced by the model.
    """

    def collect_imports(arch_file_path: str, unique_imports: set[str]) -> set[str]:
        unique_imports.add(arch_file_path)
        structures = [structure for structure in YAML_CACHE.parse_file(arch_file_path) if structure.get(ROOT_KEY_IMPORT)]
        imports = [imp for root in structures for imp in root.get(ROOT_KEY_IMPORT, {}).get(DEFINITION_FIELD_FILES, [])]

        for imp in imports:
            arch_file_dir = path.dirname(path.realpath(arch_file_path))
            parse_path = path.join(arch_file_dir, imp.removeprefix(f".{path.sep}"))
            sanitized_path = sanitize_filesystem_path(parse_path)
            if sanitized_path not in unique_imports:
                unique_imports.update(collect_imports(sanitized_path, unique_imports))

        return unique_imports

    return list(collect_imports(arch_file_path, set()))
