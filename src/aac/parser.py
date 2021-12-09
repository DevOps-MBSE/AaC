"""
The AaC parser reads a yaml file, performs validation (if not suppressed) and provides
the caller with a dictionary of the content keyed by the named type.  This allows you
to find a certain type in a model by just looking for that key.
"""
import os

import yaml


def parse_file(arch_file: str) -> dict[str, dict]:
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
    for f in files:
        contents = _read_file_content(f)
        parsed_models = parsed_models | parse_str(arch_file, contents)
    return parsed_models


def parse_str(source: str, model_content: str) -> dict[str, dict]:
    """Parse a string containing one or more yaml model definitions.

    Args:
        source:  The file the content came from (to help with better logging)
        model_content:  The yaml to parse

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
        if root and "import" in root.keys():
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
