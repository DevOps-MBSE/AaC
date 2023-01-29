"""Parse Architecture-as-Code YAML files.

The AaC parser reads a YAML file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""
import logging
import yaml
from os import path, linesep
from typing import Optional
from yaml.parser import ParserError as YAMLParserError

from aac.io.constants import DEFAULT_SOURCE_URI
from aac.io.files.aac_file import AaCFile
from aac.io.parser._parser_error import ParserError
from aac.io.paths import sanitize_filesystem_path
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation


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
    definition_lists = [_parse_str(file, _read_file_content(file)) for file in _get_files_to_process(arch_file)]
    return [definition for definition_list in definition_lists for definition in definition_list]


def _parse_str(source: str, model_content: str) -> list[Definition]:
    """Parse a string containing one or more YAML model definitions.

    Args:
        source:  The file the content came from (to help with better logging)
        model_content:  The YAML to parse

    Returns:
        The AaC definitions that were built from the model contents.
    """

    def mark_to_source_location(start: yaml.error.Mark, end: yaml.error.Mark) -> SourceLocation:
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

    yaml_tokens = _scan_yaml(model_content)
    value_tokens = [token for token in yaml_tokens if hasattr(token, "value")]
    doc_start_token = [token for token in yaml_tokens if isinstance(token, yaml.tokens.StreamStartToken)]
    doc_end_token = [token for token in yaml_tokens if isinstance(token, yaml.tokens.StreamEndToken)]
    doc_segment_tokens = [token for token in yaml_tokens if isinstance(token, yaml.tokens.DocumentStartToken)]
    doc_tokens = [*doc_start_token, *doc_segment_tokens, *doc_end_token]

    source_files: dict[str, AaCFile] = {}
    definitions: list[Definition] = []
    for doc_token_index in range(0, len(doc_tokens) - 1):
        start_doc_token = doc_tokens[doc_token_index]
        end_doc_token = doc_tokens[doc_token_index + 1]

        content_start_line = start_doc_token.start_mark.line
        content_end_line = end_doc_token.end_mark.line

        end_of_file_offset = 1 if isinstance(end_doc_token, yaml.tokens.StreamEndToken) else 0

        yaml_text = linesep.join(model_content.splitlines()[content_start_line:content_end_line + end_of_file_offset])
        yaml_text += linesep

        if yaml_text.strip():
            definition_lexemes = get_lexemes_for_definition(value_tokens, content_start_line, content_end_line)
            root_yaml, *_ = _parse_yaml(source, yaml_text)

            if "import" in root_yaml:
                del root_yaml["import"]

            root_type, *_ = root_yaml.keys()
            definition_name = root_yaml.get(root_type, {}).get("name")
            source_file = source_files.get(source)

            if not source_file:
                source_file = AaCFile(source, True, False)
                source_files[source] = source_file

            definitions.append(Definition(definition_name, yaml_text, source_file, definition_lexemes, root_yaml))
        else:
            logging.info(f"Skipping empty content between {start_doc_token}:L{content_start_line} and {end_doc_token}:L{content_end_line} in source {source}")
            logging.debug(f"Source: {source} Content:{model_content}")
            logging.debug(f"Content lines:{model_content.splitlines()}")

    return definitions


def _parse_yaml(source: str, content: str) -> list[dict]:
    """Parse content as a YAML string and return the resulting structure.

    Args:
        source (str): The source of the YAML content. Used to provide better error messages.
        content (str): The YAML content to be parsed.

    Returns:
        The parsed YAML content.

    Raises:
        If the YAML is invalid, a ParserError is raised.
        If the model is not a dictionary, a ParserError is raised.
        If the model does not have (at least) a "name" field, a ParserError is raised.
    """
    try:
        models = list(yaml.load_all(content, Loader=yaml.SafeLoader))
        _error_if_not_yaml(source, content, models)
        _error_if_not_complete(source, content, models)
        return models
    except YAMLParserError as error:
        raise ParserError(source, [f"Failed to parse file, invalid YAML {error.context} {error.problem}", content])
    except Exception as error:
        raise ParserError(source, [f"Failed to parse file, invalid YAML {error}", content])


def _scan_yaml(content):
    return list(yaml.scan(content, Loader=yaml.SafeLoader))


def _error_if_not_yaml(source, content, models):
    """Raise a ParserError if the model is not a YAML model we can parse."""

    def is_model(model):
        """Return True if the model is further parseable."""
        return isinstance(model, dict)

    # Iterate over each model and test if it is considered a valid model.
    if not all(map(is_model, models)):
        raise ParserError(source, ["provided content was not YAML", content])


def _error_if_not_complete(source, content, models):
    """Raise a ParserError if the model is incomplete."""

    def is_import(model):
        """Return True if the model is an import declaration."""
        type, *_ = model.keys()
        return type == "import"

    def assert_definition_has_name(model):
        """Throws a ParserError if the definition doesn't have a name property."""
        type, *_ = model.keys()
        has_name = model.get(type) and model.get(type).get("name")
        if not has_name:
            raise ParserError(source, [f"Definition is missing field 'name': {content}"])

    # Raise an error if any of the loaded YAML models are incomplete.
    models_without_imports = list(filter(lambda m: not is_import(m), models))
    all(map(assert_definition_has_name, models_without_imports))


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
    content = _read_file_content(arch_file_path)
    roots = _parse_yaml(arch_file_path, content)
    roots_with_imports = [root for root in roots if "import" in root.keys()]

    for root in roots_with_imports:
        for imp in root["import"]:
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
