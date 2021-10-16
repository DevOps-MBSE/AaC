"""
The AaC parser reads a yaml file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""
import os

import yaml

from aac import validator


def parse_file(arch_file: str, validate: bool = True) -> dict[str, dict]:
    """
    The parse method takes a path to an Arch-as-Code YAML file, parses it,
    and optionally validates it (default is to perform validation).

    The parse method returns a dict of each root type defined in the Arch-as-Code spec.

    If an invalid YAML file is provided and validation is performed, an error message
    and an exception being thrown.
    """
    parsed_models: dict[str, dict] = {}

    files = _get_files_to_process(arch_file)
    for f in files:
        contents = _read_file_content(f)
        parsed_models = parsed_models | parse_str(contents, arch_file, False)

    if validate:
        error_messages = validator.get_all_errors(parsed_models)

        if error_messages:
            print("Failed to validate {}: {}".format(arch_file, error_messages))
            raise RuntimeError("Failed to validate {}".format(arch_file), error_messages)

    return parsed_models


def parse_str(model_content: str, source: str, validate: bool = True) -> dict[str, dict]:
    """
    Parse a string containing one or more yaml model definitions.

    Args:
        model_content:  The yaml to parse
        source:  The file the content came from (to help with better logging)
        validate: defaults true, but can be used to disable validation

    Returns:
        A dictionary of the parsed model(s).  The key is the type name from the model and the
        value is the parsed model root.
    """
    parsed_models = {}

    roots = yaml.load_all(model_content, Loader=yaml.FullLoader)
    for root in roots:
        if "import" in root:
            del root["import"]
        root_name = list(root.keys())[0]
        parsed_models[root[root_name]["name"]] = root

    if validate:
        error_messages = validator.get_all_errors(parsed_models)

        if error_messages:
            print("Failed to validate {}: {}".format(source, error_messages))
            raise RuntimeError("Failed to validate {}".format(source), error_messages)

    return parsed_models


def _read_file_content(arch_file: str) -> str:
    """
    The read file content method extracts text content from the specified file.

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
    """
    The get files to process method traverses the import path starting from
    the specified Arch-as-Code file and returns a list of all files referenced
    by the model.
    """

    ret_val = [arch_file_path]
    content = _read_file_content(arch_file_path)
    roots = yaml.load_all(content, Loader=yaml.FullLoader)
    for root in roots:
        if "import" in root.keys():
            for imp in root["import"]:
                # parse the imported files
                parse_path = ""
                if imp.startswith("."):
                    # handle relative path
                    arch_file_dir = os.path.dirname(os.path.realpath(arch_file_path))
                    parse_path = os.path.join(arch_file_dir, imp)
                else:
                    parse_path = imp
                for append_me in _get_files_to_process(parse_path):
                    ret_val.append(append_me)

    return ret_val
