"""Parse Architecture-as-Code YAML files.

The AaC parser reads a YAML file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""
import logging

from copy import deepcopy
from yaml import Mark, Token, StreamStartToken, StreamEndToken, DocumentStartToken
from os import path, linesep
from typing import Optional

from aac.io.constants import DEFAULT_SOURCE_URI
from aac.io.files.aac_file import AaCFile
from aac.io.parser._cache_manager import get_cache
from aac.io.paths import sanitize_filesystem_path
from aac.lang.constants import DEFINITION_FIELD_NAME, DEFINITION_FIELD_IMPORT
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation


YAML_CACHE = get_cache()


def parse(source: str, source_uri: Optional[str] = None) -> list[Definition]:
    """Parse the Architecture-as-Code (AaC) definition(s) from the provided source.

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
    """Parse an Architecture-as-Code YAML file and return the definitions in it.

    Args:
        arch_file (str): The Architecture-as-Code YAML file to be parsed.

    Returns:
        The AaC definitions extracted from the specified file.
    """
    # This import is located here because the inheritance module uses the language context for lookup,
    #   causing a circular dependency at initialization
    from aac.io.parser import ParserError
    try:
        definition_lists = [_parse_str(file, _read_file_content(file)) for file in _get_files_to_process(arch_file)]
        aac_definitions = [definition for definition_list in definition_lists for definition in definition_list]
    except TypeError as error:
        print("hit type error in parse-source in _parse_file()")
    except ParserError as error:
        print("hit parser error in parse_source in _parse_file()")
        print(f"error source: {error.source} \n errors: {error.errors}")
        raise ParserError(error.source, error.errors)
    else:
        return aac_definitions


def _parse_str(source: str, model_content: str) -> list[Definition]:
    """Parse a string containing one or more YAML model definitions.

    Args:
        source:  The file the content came from (to help with better logging)
        model_content:  The YAML to parse

    Returns:
        The AaC definitions that were built from the model contents.
    """
    # This import is located here because the inheritance module uses the language context for lookup,
    #   causing a circular dependency at initialization
    from aac.io.parser import ParserError

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

    try:
        yaml_tokens: list[Token] = YAML_CACHE.scan_string(model_content)
        value_tokens: list[Token] = [token for token in yaml_tokens if hasattr(token, "value")]
        doc_start_token: list[StreamStartToken] = [token for token in yaml_tokens if isinstance(token, StreamStartToken)]
        doc_end_token: list[StreamEndToken] = [token for token in yaml_tokens if isinstance(token, StreamEndToken)]
        doc_segment_tokens: list[DocumentStartToken] = [token for token in yaml_tokens if isinstance(token, DocumentStartToken)]
        doc_tokens = [*doc_start_token, *doc_segment_tokens, *doc_end_token]

        yaml_dicts: list[dict] = deepcopy(YAML_CACHE.parse_string(model_content))
    except TypeError as error:
        print("hit type error in parse_source, parse_str()")
    except ParserError as error:
        print("hit parser error in parse_source in _parse_str()")
        print(f"error source: {error.source} \n errors: {error.errors}")
        raise ParserError(error.source, error.errors)
    else:
        source_files: dict[str, AaCFile] = {}
        definitions: list[Definition] = []
        for doc_token_index in range(0, len(doc_tokens) - 1):
            start_doc_token = doc_tokens[doc_token_index]
            end_doc_token = doc_tokens[doc_token_index + 1]

            content_start_line = start_doc_token.start_mark.line
            content_end_line = end_doc_token.end_mark.line

            end_of_file_offset = 1 if isinstance(end_doc_token, StreamEndToken) else 0

            yaml_text = linesep.join(model_content.splitlines()[content_start_line: content_end_line + end_of_file_offset])
            yaml_text += linesep

            if yaml_text.strip():
                definition_lexemes = get_lexemes_for_definition(value_tokens, content_start_line, content_end_line)

                if yaml_dicts:
                    root_yaml = yaml_dicts.pop(0)

                    definition_imports = root_yaml.get(DEFINITION_FIELD_IMPORT, [])
                    root_type, *_ = [key for key in root_yaml.keys() if key != DEFINITION_FIELD_IMPORT]
                    definition_name = root_yaml.get(root_type, {}).get(DEFINITION_FIELD_NAME)
                    source_file = source_files.get(source)

                    if not source_file:
                        source_file = AaCFile(source, True, False)
                        source_files[source] = source_file

                    new_definition = Definition(
                        name=definition_name,
                        content=yaml_text,
                        source=source_file,
                        meta_structure=None,
                        lexemes=definition_lexemes,
                        structure=root_yaml,
                        imports=definition_imports,
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
    arch_file_path = arch_file
    with open(arch_file_path, "r") as file:
        return file.read()


def _recurse_imports(arch_file_path: str, existing: set) -> set:
    """Recursive portion of _get_files_to_process that keeps track of history so that we can handle circular imports.

    Discovered an issue during testing where if there exists a cycle in the import sequence across files, the parser
    will recurse until it crashes.  Unfortunately this led to an error message to the user saying the initial file was
    invalid yaml, which it was not, creating confusion.  Now this just eliminates duplications when discovered in the
    import sequence avoiding the issue.
    """
    existing.add(arch_file_path)
    roots = YAML_CACHE.parse_file(arch_file_path)
    roots_with_imports = [root for root in roots if DEFINITION_FIELD_IMPORT in root.keys()]

    for root in roots_with_imports:
        for imp in root[DEFINITION_FIELD_IMPORT]:
            arch_file_dir = path.dirname(path.realpath(arch_file_path))
            parse_path = path.join(arch_file_dir, imp.removeprefix(f".{path.sep}"))
            sanitized_path = sanitize_filesystem_path(parse_path)
            if sanitized_path not in existing:
                existing.update(_recurse_imports(sanitized_path, existing))

    return existing


def _get_files_to_process(arch_file_path: str) -> list[str]:
    """Return a list of all files referenced in the model.

    Traverse the import path starting from the specified Arch-as-Code file and returns a list of
    all files referenced by the model.
    """
    return list(_recurse_imports(arch_file_path, set()))
