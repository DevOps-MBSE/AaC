"""AaC Plugin implementation module for the Version plugin."""

from os import path, makedirs, walk, remove
import importlib
from typing import Callable
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
from aac.context.definition import Definition
from aac.in_out.parser._parse_source import parse
from aac.plugins.generate.helpers.python_helpers import (
    get_path_from_package,
    get_python_name,
)

plugin_name = "Generate"


def generate(  # noqa: C901
    aac_file: str,
    generator_file: str,
    code_output: str,
    test_output: str,
    doc_output: str,
    no_prompt: bool,
    force_overwrite: bool,
    evaluate: bool,
) -> ExecutionResult:
    """Generate content from your AaC architecture."""

    result = ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])

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
    parsed_definitions = parse(
        aac_file
    )  # we only want to parse, not load, to avoid chicken and egg issues
    generator_definitions = context.parse_and_load(generator_file)

    # go through each generator in the parsed_definitions
    for definition in generator_definitions:
        if definition.get_root_key() != "generator":
            continue
        generator = definition.instance

        # go through each generator source and get data from parsed_definitions based on from_source

        for source in generator.sources:
            source_data_definitions: list[Definition] = []
            for parsed_definition in parsed_definitions:
                if parsed_definition.get_root_key() == source.data_source:
                    source_data_definitions.append(parsed_definition)

            if not source_data_definitions or len(source_data_definitions) == 0:
                # no data for this particular generator
                continue

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
                    source_data_structures = []
                    source_data_package = source_data_def.package
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
                        jinja_output = jinja_template.render(source_data_structure)
                        output = jinja_output
                        if template.output_file_extension == "py":
                            output = black.format_str(jinja_output, mode=black.Mode())

                        # write output to files to the traget in the template, respecting the overwrite indicator
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
                            evaluate_file_path = f"{output_file_path}.aac_evaluate"
                            with open(evaluate_file_path, "w") as output_file:
                                output_file.write(output)
                                output_file.close()
                        else:
                            # write contents to output_file_path
                            if force_overwrite or template.overwrite in [
                                context.create_aac_enum(
                                    "aac.lang.OverwriteOption", "OVERWRITE"
                                )
                            ]:
                                if path.exists(output_file_path):
                                    backup_file(output_file_path)
                                with open(output_file_path, "w") as output_file:
                                    output_file.write(output)
                                    output_file.close()
                            elif template.overwrite in [
                                context.create_aac_enum(
                                    "aac.lang.OverwriteOption", "SKIP"
                                )
                            ]:
                                # this is for the skip option, so only write if file doesn't exist
                                if not path.exists(output_file_path):
                                    with open(output_file_path, "w") as output_file:
                                        output_file.write(output)
                                        output_file.close()
                                else:
                                    evaluate_file_path = (
                                        f"{output_file_path}.aac_evaluate"
                                    )
                                    with open(evaluate_file_path, "w") as output_file:
                                        output_file.write(output)
                                        output_file.close()

    return result


def clean(
    aac_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool
) -> ExecutionResult:
    """Clean up generated code, tests, and docs."""
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
    """Returns the output directories for code, tests, and docs."""
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

    return (code_out, test_out, doc_out)


def get_output_file_path(
    root_output_directory: str,
    generator_template,
    source_package: str,
    source_name: str,
) -> str:
    """Returns the output file path for a generator template."""
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
    return path.abspath(result)


def get_callable(package_name: str, file_name: str, function_name: str) -> Callable:
    """Returns a callable function from a package, file, and function name."""
    module = importlib.import_module(f"{package_name}.{file_name}")
    return getattr(module, function_name)


def load_template(
    template_abs_path: str, helper_functions: dict[str, Callable] = {}
) -> Template:
    """Load a jinja2 template from a file."""
    env = Environment(loader=FileSystemLoader("/"))
    env.globals.update(helper_functions)
    template = env.get_template(template_abs_path)
    return template


def backup_file(file_path: str) -> str:
    """Backs up a file by appending .aac_backup to the file name."""
    backup_file_path = f"{file_path}.aac_backup"
    with open(file_path, "r") as input_file:
        with open(backup_file_path, "w") as backup_file:
            backup_file.write(input_file.read())
    return backup_file_path
