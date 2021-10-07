import ArchValidator
import os
import yaml


def parse(archFile: str, validate=True):
    """
    The parse method takes a path to an Arch-as-Code YAML file, parses it,
    and optionally validates it (default is to perform validation).

    The parse method returns a dict of each root type defined in the Arch-as-Code spec.

    If an invalid YAML file is provided and validation is performed, an error message
    and an exception being thrown.
    """

    enum_types = {}
    data_types = {}
    model_types = {}
    use_case_types = {}
    ext_types = {}

    files = _get_files_to_process(archFile)
    for f in files:
        contents = _read_file_content(f)
        roots = yaml.load_all(contents, Loader=yaml.FullLoader)
        for root in roots:
            _process_root(root, model_types, data_types, enum_types, use_case_types, ext_types)

    if validate:
        isValid, errMsg = ArchValidator.validate(model_types, data_types, enum_types, use_case_types, ext_types)

        if not isValid:
            print("Failed to validate {}: {}".format(archFile, errMsg))
            raise RuntimeError("Failed to validate {}".format(archFile), errMsg)

    return model_types, data_types, enum_types, use_case_types, ext_types


def _read_file_content(archFile):
    """
    The read file content method extracts text content from the specified file.
    """

    # arch_file_path = os.path.dirname(os.path.realpath(archFile))
    arch_file_path = archFile
    content = ""
    with open(arch_file_path, 'r') as file:
        content = file.read()
    return content


def _get_files_to_process(arch_file_path):
    """
    The get files to process method traverses the import path starting from
    the specified Arch-as-Code file and returns a list of all files referenced
    by the model.
    """

    retVal = [arch_file_path]
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
                    retVal.append(append_me)

    return retVal


def _process_root(root, model_types, data_types, enum_types, use_case_types, ext_types):
    """
    The process root method takes a single root dict and adds it to the the
    root type dict keyed by the name of the modeled root.
    """

    # TODO This is a bit "clunky".  Could I just collapse all these into a single dict, ignoring the root type?
    #      Or maybe have a dict keyed by type and then name?  Not sure if these would be a better dev experience.

    # ignore import root type
    if "enum" in root.keys():
        enum_types[root["enum"]["name"]] = root
    if "data" in root.keys():
        data_types[root["data"]["name"]] = root
    if "model" in root.keys():
        model_types[root["model"]["name"]] = root
    if "usecase" in root.keys():
        use_case_types[root["usecase"]["title"]] = root
    if "extension" in root.keys():
        ext_types[root["extension"]["name"]] = root
