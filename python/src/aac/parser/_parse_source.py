"""Parse Architecture-as-Code YAML files.

The AaC parser reads a YAML file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""

from os import path
import yaml
from yaml.parser import ParserError as YAMLParserError

from aac.parser._parser_error import ParserError
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation


def parse(source: str) -> list[Definition]:
    """Parse the Architecture-as-Code (AaC) definition(s) from the provided source.

    Args:
        source (str): Must be either a file path to an AaC yaml file or a string containing AaC definitions.

    Returns:
        A list of Definition objects containing the internal representation of the definition and metadata
        associated with the definition.
    """

    def mark_to_source_location(start: yaml.error.Mark, end: yaml.error.Mark) -> SourceLocation:
        return SourceLocation(start.line, start.column, start.index, end.column - start.column)

    def get_lexemes_for_definition(contents):
        yaml_source = path.abspath(source) if path.lexists(source) else "<string>"
        lexemes = []
        tokens = [token for token in yaml.scan(contents, Loader=yaml.SafeLoader)]
        for token in tokens:
            if hasattr(token, "value"):
                location = mark_to_source_location(token.start_mark, token.end_mark)
                lexemes.append(Lexeme(location, yaml_source, token.value))
        return lexemes

    contents = get_yaml_from_source(source)
    definitions = _parse_file(source) if path.lexists(source) else _parse_str(source, contents)

    parsed_definitions = []
    for name, definition in definitions.items():
        parsed_definitions.append(Definition(name, contents, get_lexemes_for_definition(contents), definition))

    return parsed_definitions


def get_yaml_from_source(source: str) -> str:
    """Get the YAML contents from the provided source.

    Args:
        source (str): The source from which to get the YAML contents. This can be a path-like
        string pointing to a file with YAML contents; or a string of YAML contents.

    Returns:
        The YAML contents extracted from source.
    """
    if path.lexists(source):
        return _read_file_content(source)
    return source


def _parse_file(arch_file: str) -> dict[str, dict]:
    """Parse an Architecture-as-Code YAML file.

    Args:
        arch_file (str): The Architecture-as-Code YAML file to be parsed.

    Returns:
        The parse method returns a dict of each root type defined in the Arch-as-Code spec. If
        validation of the provided YAML file fails, an error message is displayed and None is
        returned.
    """
    parsed_models: dict[str, dict] = {}

    files = _get_files_to_process(arch_file)
    for file in files:
        contents = _read_file_content(file)
        parsed_models = parsed_models | _parse_str(arch_file, contents)
    return parsed_models


def _parse_str(source: str, model_content: str) -> dict[str, dict]:
    """Parse a string containing one or more YAML model definitions.

    Args:
        source:  The file the content came from (to help with better logging)
        model_content:  The YAML to parse

    Returns:
        A dictionary of the parsed model(s). The key is the type name from the model and the
        value is the parsed model root.
    """
    parsed_models = {}

    roots = _parse_yaml(source, model_content)
    for root in roots:
        if "import" in root:
            del root["import"]

        root_type, *_ = root.keys()
        root_name = root.get(root_type).get("name")
        parsed_models = parsed_models | {root_name: root}
    return parsed_models


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
    content = ""
    with open(arch_file_path, "r") as file:
        content = file.read()
    return content


def _get_files_to_process(arch_file_path: str) -> list[str]:
    """Return a list of all files referenced in the model.

    Traverse the import path starting from the specified Arch-as-Code file and returns a list of
    all files referenced by the model.
    """
    ret_val = [arch_file_path]
    content = _read_file_content(arch_file_path)
    roots = _parse_yaml(arch_file_path, content)
    for root in roots:
        if "import" in root.keys():
            for imp in root["import"]:
                # parse the imported files
                parse_path = ""
                if imp.startswith("."):
                    # handle relative path
                    arch_file_dir = path.dirname(path.realpath(arch_file_path))
                    parse_path = path.join(arch_file_dir, imp)
                else:
                    parse_path = imp
                for append_me in _get_files_to_process(parse_path):
                    ret_val.append(append_me)

    return ret_val
