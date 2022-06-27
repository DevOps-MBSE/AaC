"""Parse Architecture-as-Code YAML files.

The AaC parser reads a YAML file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""

from os import path
import yaml
from yaml.parser import ParserError as YAMLParserError
from typing import Optional

from aac.files.aac_file import AaCFile
from aac.parser._parser_error import ParserError
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation


YAML_DOCUMENT_SEPARATOR = "---"
DEFAULT_SOURCE_URI = "<string>"


def parse(source: str, source_uri: Optional[str] = None) -> list[Definition]:
    """Parse the Architecture-as-Code (AaC) definition(s) from the provided source.

    Args:
        source (str): Must be either a file path to an AaC yaml file or a string containing AaC definitions.
        source_uri (Optional[str]): Overrides and sets the source_uri

    Returns:
        A list of Definition objects containing the internal representation of the definition and metadata
        associated with the definition.
    """
    return _parse_file(source) if path.lexists(source) else _parse_str(source_uri or DEFAULT_SOURCE_URI, source)


def _parse_file(arch_file: str) -> list[Definition]:
    """Parse an Architecture-as-Code YAML file and return the definitions in it.

    Args:
        arch_file (str): The Architecture-as-Code YAML file to be parsed.

    Returns:
        The AaC definitions extracted from the specified file.
    """
    definitions: list[Definition] = []

    for file in _get_files_to_process(arch_file):
        definitions.extend(_parse_str(file, _read_file_content(file)))

    return definitions


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

    def get_lexemes_for_definition(contents):
        yaml_source = path.abspath(source) if path.lexists(source) else DEFAULT_SOURCE_URI
        lexemes = []
        tokens = [token for token in yaml.scan(contents, Loader=yaml.SafeLoader) if hasattr(token, "value")]
        for token in tokens:
            location = mark_to_source_location(token.start_mark, token.end_mark)
            lexemes.append(Lexeme(location, yaml_source, token.value))
        return lexemes

    source_files = {}
    definitions: list[Definition] = []
    for doc in model_content.split(YAML_DOCUMENT_SEPARATOR):
        for root in _parse_yaml(source, doc):
            if "import" in root:
                del root["import"]

            root_type, *_ = root.keys()
            root_name = root.get(root_type).get("name")
            contents = _add_yaml_document_separator(doc) if _has_document_separator(model_content, doc) else doc
            lexemes = get_lexemes_for_definition(contents)
            source_file = source_files.get(source)

            if not source_file:
                source_file = AaCFile(source, True, True)
                source_files[source] = source_file

            definitions.append(Definition(root_name, contents, source_file, lexemes, root))

    return definitions


def _has_document_separator(model_content: str, document: str) -> bool:
    before, _, _ = model_content.partition(document)
    return before.endswith(YAML_DOCUMENT_SEPARATOR)


def _parse_yaml(source: str, content: str) -> dict:
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
        raise ParserError(source, [f"invalid YAML {error.context} {error.problem}", content])


def _error_if_not_yaml(source, content, models):
    """Raise a ParserError if the model is not a YAML model we can parse."""

    def is_model(model):
        """Return True if the model is further parseable."""
        return isinstance(model, dict)

    # Iterate over each model and test if it is considered a valid model.
    if False in map(is_model, models):
        raise ParserError(source, ["provided content was not YAML", content])


def _error_if_not_complete(source, content, models):
    """Raise a ParserError if the model is incomplete."""

    def is_import(model):
        """Return True if the model is an import declaration."""
        type, *_ = model.keys()
        return type == "import"

    def is_complete_model(model):
        """Return True if the model has a name property; False, otherwise."""
        type, *_ = model.keys()
        return model.get(type) and model.get(type).get("name")

    # Raise an error if any of the loaded YAML models are incomplete.
    models_no_imports = list(filter(lambda m: not is_import(m), models))
    if not all(map(is_complete_model, models_no_imports)):
        raise ParserError(source, [f"incomplete model:\n{content}\n"])


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


def _get_files_to_process(arch_file_path: str) -> list[str]:
    """Return a list of all files referenced in the model.

    Traverse the import path starting from the specified Arch-as-Code file and returns a list of
    all files referenced by the model.
    """
    ret_val = [arch_file_path]
    content = _read_file_content(arch_file_path)
    roots = _parse_yaml(arch_file_path, content)
    roots_with_imports = filter(lambda r: "import" in r.keys(), roots)

    for root in roots_with_imports:
        for imp in root["import"]:
            arch_file_dir = path.dirname(path.realpath(arch_file_path))
            parse_path = path.join(arch_file_dir, imp.removeprefix(f".{path.sep}"))
            ret_val.extend(_get_files_to_process(parse_path))

    return ret_val


def _add_yaml_document_separator(content: str) -> str:
    """Add the YAML document separator to the content."""
    content = content.lstrip()
    return f"{YAML_DOCUMENT_SEPARATOR}\n{content}" if content else content
