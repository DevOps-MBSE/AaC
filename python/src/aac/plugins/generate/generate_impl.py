"""AaC Plugin implementation module for the Version plugin."""

import logging
from os import path, makedirs, walk, remove
import importlib
from typing import Callable, Any
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    OperationCancelled,
    ExecutionError,
    ExecutionMessage,
    MessageLevel,
)
from jinja2 import Environment, FileSystemLoader, Template
import black
from aac.context.language_context import LanguageContext
from aac.context.language_error import LanguageError
from aac.context.definition import Definition
from aac.in_out.parser._parse_source import parse
from aac.in_out.paths import sanitize_filesystem_path
from aac.plugins.generate.helpers.python_helpers import (
    get_path_from_package,
    get_python_name,
)
from aac.in_out.parser._parser_error import ParserError


plugin_name = "Generate"


def _write_to_file(file_path: str, content: str):
    """
    Opens, writes to, and closes a file.

    Args:
        file_path (str): File path to be written to.
        content (str): Content to be written to file.

    Exceptions:
        IOError: Exception raised when the file path cannot be parsed.
        Exception: Generic exception raised when an unexpected error is encountered.
    """
    try:
        with open(file_path, "w") as output_file:
            output_file.write(content)
            output_file.close()
    except IOError as error:
        logging.error(f"Failed to parse {file_path} with error {error}")
    except Exception as error:
        # Catch-all for any unknown and unexpected errors with opening and reading files.
        logging.error(f"Unexpected error when opening {file_path} with {error}")


def output_to_jinja_template(
    evaluate: bool,
    force_overwrite: bool,
    source: Any,
    template: Any,
    jinja_template: Template,
    code_out_dir: str,
    test_out_dir: str,
    doc_out_dir: str,
    source_data_structure: dict,
    source_data_def: Definition
):
    """
    Outputs generation data to a jinja2 template file.

    Args:
        evaluate (bool): Command argument from the generate command.  If true, generate only writes evaluation files with no impact to existing files.
        force_overwrite (bool): Command argument from the generate command.  If true, forces generate to overwrite any already existing files.
        source (Any): An instance of the source generator file definition.
        template (Any): An instance of the generator template definition.
        jinja_template (Template): Jinja2 template file.
        code_out_dir (str): Output path for generated code files.
        test_out_dir (str): Output path for generated test files.
        doc_out_dir (str): Output path for generated doc files.
        source_data_structure (dict): A dictionary containing the source data structure.
        source_data_def (Definition): The definition of the source aac data.
    """
    context = LanguageContext()
    source_data_package = source_data_def.package
    jinja_output = jinja_template.render(source_data_structure)
    output = black.format_str(jinja_output, mode=black.Mode()) if template.output_file_extension == "py" else jinja_output

    # write output to files to the target in the template, respecting the overwrite indicator
    root_out_dir = code_out_dir
    if template.output_target == context.create_aac_enum(
        "aac.lang.GeneratorOutputTarget", "TEST"
    ):
        root_out_dir = test_out_dir
    elif template.output_target == context.create_aac_enum(
        "aac.lang.GeneratorOutputTarget", "DOC"
    ):
        root_out_dir = doc_out_dir
    file_name = source_data_def.name
    if source.data_content:
        name_extension = f"{source_data_structure['name'].replace(' ', '_').replace('-', '_')}"
        file_name = f"{file_name}_{name_extension}"
    output_file_path = get_output_file_path(
        root_out_dir, template, source_data_package, file_name
    )
    # make sure the directory exists
    output_dir = path.dirname(output_file_path)
    if not path.exists(output_dir):
        makedirs(output_dir)

    if evaluate:
        # write contents to an aac_evaluate file for user review
        _write_to_file(f"{output_file_path}.aac_evaluate", output)
    else:
        # write contents to output_file_path
        if force_overwrite or template.overwrite in [
            context.create_aac_enum(
                "aac.lang.OverwriteOption", "OVERWRITE"
            )
        ]:
            if path.exists(output_file_path):
                backup_file(output_file_path)
            _write_to_file(output_file_path, output)
        elif template.overwrite in [
            context.create_aac_enum(
                "aac.lang.OverwriteOption", "SKIP"
            )
        ]:
            # this is for the skip option, so only write if file doesn't exist
            if not path.exists(output_file_path):
                _write_to_file(output_file_path, output)
            else:
                evaluate_file_path = (
                    f"{output_file_path}.aac_evaluate"
                )
                _write_to_file(evaluate_file_path, output)


def generate_content(
    evaluate: bool,
    force_overwrite: bool,
    source: Any,
    template: Any,
    jinja_template: Template,
    code_out_dir: str,
    test_out_dir: str,
    doc_out_dir: str,
    source_data_def: Definition
):
    """
    Generates file content for use by the jinja template.

    Args:
        evaluate (bool): Command argument from the generate command.  If true, generate only writes evaluation files with no impact to existing files.
        force_overwrite (bool): Command argument from the generate command.  If true, forces generate to overwrite any already existing files.
        source (Any): An instance of the source generator file definition.
        template (Any): An instance of the generator template definition.
        jinja_template (Template): Jinja2 template file.
        code_out_dir (str): Output path for generated code files.
        test_out_dir (str): Output path for generated test files.
        doc_out_dir (str): Output path for generated doc files.
        source_data_def (Definition): The definition of the source aac data.

    Raises:
        ExecutionError: When the content of the data source file is invalid.
    """
    source_data_structures = []
    if not source.data_content:
        # we'll just use the root structure
        source_data_structures = [source_data_def.structure]
    else:
        # we've got to navigate the structure to get the right data
        content_split = source.data_content.split(".")
        if content_split[0] != source_data_def.get_root_key():
            raise ExecutionError(
                f"Invalid data_content for generator source {source.name}. The data_content must be the root key of the data source."
            )
        else:
            source_data_structures = [source_data_def.structure]
            for field_name in content_split:
                new_source_data_structures = []
                for structure in source_data_structures:
                    if field_name not in structure:
                        # it is possible that fields are optional and may not be present, so continue if not present
                        continue
                    field_value = structure[field_name]
                    if isinstance(field_value, list):
                        new_source_data_structures.extend(field_value)
                    elif isinstance(field_value, dict):
                        new_source_data_structures.append(field_value)
                    else:
                        raise ExecutionError(
                            f"Invalid data_content {source.data_content} for generator source {source.name}. The data_content must be a field chain in the data source that represents a structure of data, not a primitive."
                        )
                source_data_structures = new_source_data_structures
    for source_data_structure in source_data_structures:
        output_to_jinja_template(evaluate, force_overwrite, source, template, jinja_template, code_out_dir, test_out_dir, doc_out_dir, source_data_structure, source_data_def)


def generate_data_from_source(
    evaluate: bool,
    force_overwrite: bool,
    source: Any,
    parsed_definitions: list[Definition],
    code_out_dir: str,
    test_out_dir: str,
    doc_out_dir: str,
    generator_file: str
):
    """
    Extracts data from a generator source and uses it to generate content.

    Args:
        evaluate (bool): Command argument from the generate command.  If true, generate only writes evaluation files with no impact to existing files.
        force_overwrite (bool): Command argument from the generate command.  If true, forces generate to overwrite any already existing files.
        source (Any): An instance of the source generator file definition.
        parsed_definitions (list[Definition]): List of parsed definitions to be used in file generation.
        code_out_dir (str): Output path for generated code files.
        test_out_dir (str): Output path for generated test files.
        doc_out_dir (str): Output path for generated doc files.
        generator_file (str): AaC generator file.

    """
    source_data_definitions: list[Definition] = []
    for parsed_definition in parsed_definitions:
        if parsed_definition.get_root_key() == source.data_source:
            source_data_definitions.append(parsed_definition)

    if not source_data_definitions or len(source_data_definitions) == 0:
        # no data for this particular generator
        return

    # go through each generator template
    for template in source.templates:
        # figure out how to load func_dict into the jinja2 environment
        helper_functions: dict[str, Callable] = {}
        for helper in template.helper_functions:
            helper_functions[helper.function] = get_callable(
                helper.package, helper.module, helper.function
            )

        # generate code using the template and source
        template_abs_path = path.abspath(
            path.join(path.dirname(generator_file), template.template_file)
        )
        jinja_template = None
        if len(helper_functions) > 0:
            jinja_template = load_template(template_abs_path, helper_functions)
        else:
            jinja_template = load_template(template_abs_path)

        # loop over the parsed definitions and generate content for each
        for source_data_def in source_data_definitions:
            generate_content(evaluate, force_overwrite, source, template, jinja_template, code_out_dir, test_out_dir, doc_out_dir, source_data_def)


def process_parser_error(pe: ParserError) -> str:
    """
    Process the message(s) from ParserError in a way which accounts for one or two entries.

    Args:
        pe (ParserError):  The ParserError instance to have messages extracted.

    Returns:
        str: The result constructed error_message string.
    """
    # Construct error message, we should have at least 2 entries in the list
    # but let's make sure first. If we only have one entry then use that.
    error_message = ""
    if len(pe.errors) > 1:
        error_message = str(pe.errors[0]) + str(pe.errors[1])
    elif len(pe.errors) == 1:
        error_message = str(pe.errors[0])
    return error_message


def generate(
    aac_file: str,
    generator_file: str,
    code_output: str,
    test_output: str,
    doc_output: str,
    no_prompt: bool,
    force_overwrite: bool,
    evaluate: bool,
) -> ExecutionResult:
    """
    Generate content from your AaC architecture.

    Args:
        aac_file (str):  Content to be used for generation.
        generator_file (str): AaC generator file.
        code_out_dir (str): Output path for generated code files.
        test_out_dir (str): Output path for generated test files.
        doc_out_dir (str): Output path for generated doc files.
        no_prompt (bool): Command argument.  If true, generates files with no prompt.  Primarily used for testing or by other plugins.
        force_overwrite (bool): Command argument.  If true, forces generate to overwrite any already existing files.
        evaluate (bool): Command argument.  If true, generate only writes evaluation files with no impact to existing files.

    Returns:
        ExecutionResult: The result of executing the generate command.

    Raises:
        OperationCancelled: When the operation is canceled by the user.
    """

    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])

    # setup return messages
    messages = []

    # setup definition lists
    parsed_definitions = []
    generator_definitions = []  # This may be the last line of code I ever get paid to write JSW 08APR2025

    # setup directories
    code_out_dir = ""
    test_out_dir = ""
    doc_out_dir = ""
    try:
        code_out_dir, test_out_dir, doc_out_dir = get_output_directories(
            "AaC will generate code and tests in the following directories:",
            aac_file,
            code_output,
            test_output,
            doc_output,
            no_prompt,
        )
    except OperationCancelled as e:
        result.status_code = ExecutionStatus.OPERATION_CANCELLED
        result.add_message(ExecutionMessage(e.message, MessageLevel.INFO, None, None))
        return result

    # build out properties
    # the templates need data from the plugin model to generate code
    context = LanguageContext()

    try:
        parsed_definitions = parse(
            aac_file
        )  # we only want to parse, not load, to avoid chicken and egg issues
        generator_definitions = context.parse_and_load(generator_file)  # Now we want to parse and load for real
    except LanguageError as le:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        messages.append(
            ExecutionMessage(
                message="LanguageError from parse_and_load: " + le.message + " at location: " + le.location,
                level=MessageLevel.DEBUG,
                source=aac_file,
                location=None,  # Included in the message above. Their type/format is not easily compatible with the SourceLocation needed here.
            )
        )
        return ExecutionResult(plugin_name, "generate", status, messages)
    except ParserError as pe:
        status = ExecutionStatus.PARSER_FAILURE

        messages.append(
            ExecutionMessage(
                message="ParserError from parse_and_load. " + process_parser_error(pe),
                level=MessageLevel.DEBUG,
                source=aac_file,
                location=None,  # Included in the message above. Their type/format is not easily compatible with the SourceLocation needed here.
            )
        )
        return ExecutionResult(plugin_name, "generate", status, messages)
    except Exception as ex:  # Also catching IOError but we don't do anything special handling for IOError so handle it here
        status = ExecutionStatus.GENERAL_FAILURE

        messages.append(
            ExecutionMessage(
                message="Exception from parse_and_load. " + ex.message,
                level=MessageLevel.DEBUG,
                source=aac_file,
                location=None,  # Included in the message above. Their type/format is not easily compatible with the SourceLocation needed here.
            )
        )
        return ExecutionResult(plugin_name, "generate", status, messages)

    # go through each generator in the parsed_definitions
    for definition in generator_definitions:
        if definition.get_root_key() != "generator":
            continue
        generator = definition.instance

        # go through each generator source and get data from parsed_definitions based on from_source
        for source in generator.sources:
            generate_data_from_source(evaluate, force_overwrite, source, parsed_definitions, code_out_dir, test_out_dir, doc_out_dir, generator_file)
    return result


def clean(
    aac_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool
) -> ExecutionResult:
    """
    Clean up generated code, tests, and docs.

    Args:
        aac_file (str):  Content used for generating the target files.
        code_out_dir (str): Output path for target code files.
        test_out_dir (str): Output path for target test files.
        doc_out_dir (str): Output path for target doc files.
        no_prompt (bool): Command argument.  If true, executes with no prompt.  Primarily used for testing or by other plugins.

    Returns:
        ExecutionResult: The result of executing the clean command.
    """

    # setup directories

    code_out_dir, test_out_dir, doc_out_dir = get_output_directories(
        "AaC will delete backup and eval files in the following directories:",
        aac_file,
        code_output,
        test_output,
        doc_output,
        no_prompt,
    )

    for dir in [code_out_dir, test_out_dir, doc_out_dir]:
        if path.exists(dir):
            for root, dirs, files in walk(dir):
                for file in files:
                    if file.endswith(".aac_backup") or file.endswith(".aac_evaluate"):
                        remove(path.join(root, file))

    return ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])


def get_output_directories(
    message: str,
    aac_plugin_file: str,
    code_output: str,
    test_output: str,
    doc_output: str,
    no_prompt: bool,
) -> tuple[str, str, str]:
    """
    Returns the output directories for code, tests, and docs.

    Args:
        message (str): Output message.
        aac_plugin_file (str):  Content to be used for generation.
        code_output (str): Output path for generated code files.
        test_output (str): Output path for generated test files.
        doc_output (str): Output path for generated doc files.
        no_prompt (bool): Command argument.  If true, generates files with no prompt.  Primarily used for testing or by other plugins.

    Returns:
        tuple[str, str, str]: A tuple containing the three output paths.

    Raises:
        ExecutionError: When the content of the data source file is invalid.
        OperationCancelled: When the operation is canceled by the user.
    """
    code_out: str = code_output
    test_out: str = test_output
    doc_out: str = doc_output

    if not code_output or len(code_output) == 0:
        aac_plugin_path = path.abspath(aac_plugin_file)
        if not path.exists(aac_plugin_file):
            raise ExecutionError(
                f"The provided AaC Plugin file does not exist: {aac_plugin_file}"
            )
        code_out = path.dirname(aac_plugin_path)

    if not test_output or len(test_output) == 0:
        test_out = path.dirname(path.abspath(aac_plugin_file))

    if not doc_output or len(doc_output) == 0:
        doc_out = path.dirname(path.abspath(aac_plugin_file))

    if not no_prompt:
        print(message)
        print(f"   code: {code_out}")
        print(f"   tests: {test_out}")
        print(f"   docs: {doc_out}")
        approval = "first"
        while approval not in [
            "y",
            "Y",
            "yes",
            "Yes",
            "YES",
            "n",
            "N",
            "no",
            "No",
            "NO",
        ]:
            approval = input("Do you want to continue? (y/n): ")
        if approval in ["y", "Y", "yes", "Yes", "YES"]:
            return (code_out, test_out, doc_out)
        else:
            raise OperationCancelled("User cancelled operation.")

    code_out = sanitize_filesystem_path(code_out)
    test_out = sanitize_filesystem_path(test_out)
    doc_out = sanitize_filesystem_path(doc_out)

    return (code_out, test_out, doc_out)


def get_output_file_path(
    root_output_directory: str,
    generator_template,
    source_package: str,
    source_name: str,
) -> str:
    """
    Returns the output file path for a generator template.

    Args:
        root_output_directory (str): Root directory of the output path.
        generator_template: Template for the aac generator file.
        source_package (str): Package containing the definition source.
        source_name (str): Name of the definition.

    Returns:
        str: Output file path for a generator template.
    """
    result = root_output_directory
    if generator_template.output_path_uses_data_source_package and source_package:
        context = LanguageContext()
        if generator_template.output_target == context.create_aac_enum(
            "aac.lang.GeneratorOutputTarget", "TEST"
        ):
            # this is a bit quirky, but turns out our test file path can't use the same structure as our source package or imports won't work properly
            # so for tests, we'll just add a tests_ prefix to the package name
            result = path.join(result, f"test_{get_path_from_package(source_package)}")
        else:
            result = path.join(result, get_path_from_package(source_package))
    file_name = ""
    if generator_template.output_file_prefix:
        file_name = generator_template.output_file_prefix
    if generator_template.output_file_name:
        file_name = f"{file_name}{generator_template.output_file_name}"
    elif source_name:
        file_name = f"{file_name}{get_python_name(source_name)}"
    if generator_template.output_file_suffix:
        file_name = f"{file_name}{generator_template.output_file_suffix}"
    file_name = f"{file_name}.{generator_template.output_file_extension}"
    result = path.join(result, file_name)
    return sanitize_filesystem_path(path.abspath(result))


def get_callable(package_name: str, file_name: str, function_name: str) -> Callable:
    """
    Returns a callable function from a package, file, and function name.

    Args:
        package_name (str): Package name where the function resides.
        file_name (str): File name where the function resides.
        function_name (str): Name of the Function.

    Returns:
        Callable: Callable form of the function.
    """
    module = importlib.import_module(f"{package_name}.{file_name}")
    return getattr(module, function_name)


def load_template(
    template_abs_path: str, helper_functions: dict[str, Callable] = {}
) -> Template:
    """
    Load a jinja2 template from a file.

    Args:
        template_abs_path (str): Absolute Path of the Jinja2 Template.
        helper_functions (dict[str, Callable]): Helper Functions for the template.

    Returns:
        template (Template): Jinja2 Template object.
    """
    env = Environment(loader=FileSystemLoader("/"))
    env.globals.update(helper_functions)
    template = env.get_template(template_abs_path)
    return template


def backup_file(file_path: str) -> str:
    """
    Backs up a file by appending .aac_backup to the file name.

    Args:
        file_path (str): The file being backed up.

    Returns:
        The file path to the backup file.

    Exceptions:
        IOError: Exception raised when the file path cannot be parsed.
        Exception: Generic exception raised when an unexpected error is encountered.
    """
    backup_file_path = f"{file_path}.aac_backup"
    try:
        with open(file_path, "r") as input_file:
            with open(backup_file_path, "w") as backup_file:
                backup_file.write(input_file.read())
                backup_file.close()
            input_file.close()
    except IOError as error:
        logging.error(f"Failed to parse {file_path} with error {error}")
    except Exception as error:
        # Catch-all for any unknown and unexpected errors with opening and reading files.
        logging.error(f"Unexpected error when opening {file_path} with {error}")
    return sanitize_filesystem_path(backup_file_path)
