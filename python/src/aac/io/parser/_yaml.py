"""YAML-specific parsing and scanning functions."""
import logging
import traceback

from yaml import scan, load_all, SafeLoader, Token
from yaml.parser import ParserError as YAMLParserError
from yaml.scanner import ScannerError as YAMLScannerError

from aac.io.parser._parser_error import ParserError


def scan_yaml(content: str) -> list[Token]:
    """Parse the YAML string and produce a list of scanning tokens."""
    return list(scan(content, Loader=SafeLoader))


def parse_yaml(source: str, content: str) -> list[dict]:
    """Parse content as a YAML string and return the resulting structure.

    Be sure to use the YAML Parser Cache instead of this function.

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
        models = list(load_all(content, Loader=SafeLoader))
        _error_if_not_yaml(source, content, models)
        _error_if_not_complete(source, content, models)
        return models
    except YAMLParserError as error:
        traceback.print_exc(limit=0)
        logging.error(f"Encountered YAML Parsing Error-Problem: {error.problem}. Encountered in: {source} at {error.context}")
        if error.problem_mark:
            logging.error(f"Error occurs at line, column: {error.problem_mark.line+1}, {error.problem_mark.column+1}")
        logging.error(f"Content of error: {content}")
        raise ParserError(f"Failed to parse file: {source}", [f"Encountered the following parser error: {error.problem}",
                                                              f"Encountered error at line, column: {error.problem_mark.line+1}, {error.problem_mark.column+1}",
                                                              f"Context of the error: {error.context}"])
    except YAMLScannerError as error:
        traceback.print_exc(limit=0)
        logging.error(f"Encountered YAML Scanner Error-Problem: {error.problem}. Encountered in: {source} at {error.context}")
        if error.problem_mark:
            logging.error(f"Error occurs at line, column: {error.problem_mark.line+1}, {error.problem_mark.column+1}")
        logging.error(f"Content of error: {content}")
        raise ParserError(f"Failed to parse file: {source}", [f"Encountered the following scanner error: {error.problem}",
                                                              f"Encountered error at line, column: {error.problem_mark.line+1}, {error.problem_mark.column+1}",
                                                              f"Context of the error: {error.context}"])
    except Exception as error:
        traceback.print_exc(limit=0)
        logging.error(f"Error: {error}. Encountered in: {source}")
        logging.error(f"Content of error: {content}")
        raise ParserError(f"Failed to parse file: {source}", [f"Encountered the following error: {error}"])


def _error_if_not_yaml(source, content, models):
    """Raise a ParserError if the model is not a YAML model we can parse."""

    def is_model(model):
        """Return True if the model is further parsable."""
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
