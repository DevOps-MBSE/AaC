"""AaC Plugin implementation module for the Version plugin."""

from os import path
import importlib
from typing import Callable, Any
import filecmp
import difflib
import shutil
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus, OperationCancelled, ExecutionError
from jinja2 import Environment, FileSystemLoader, Template
from aac.context.language_context import LanguageContext
from aac.lang.generatorsource import GeneratorSource
from aac.lang.generatortemplate import GeneratorTemplate
from aac.lang.generatoroutputtarget import GeneratorOutputTarget
from aac.lang.overwriteoption import OverwriteOption
from aac.plugins.generate.helpers.python_helpers import get_path_from_package

plugin_name = "Generate Plugin"


def generate(aac_file: str, generator_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool) -> ExecutionResult:
    """Generate content from your AaC architecture."""

    print(f"DEBUG: Running the AaC Genenerate with:\n   aac_plugin_file: {aac_file}\n   generator_file: {generator_file}\n   code_output: {code_output}\n   test_output: {test_output}\n   doc_output: {doc_output}\n   no_prompt: {no_prompt}")

    # setup directories
    code_out_dir, test_out_dir, doc_out_dir = get_output_directories(aac_file, code_output, test_output, doc_output, no_prompt)

    print(f"DEBUG: code_out_dir: {code_out_dir} test_out_dir: {test_out_dir}")

    # build out properties
    # the templates need data from the plugin model to generate code
    context = LanguageContext()
    parsed_definitions = context.parse_and_load(aac_file)
    generator_definitions = context.parse_and_load(generator_file)

    # go through each generator in the parsed_definitions
    for definition in generator_definitions:
        generator = definition.instance

        # go through each generator source and get data from parsed_definitions based on from_source
        for source in generator.sources:
            source_data = {}
            for parsed_definition in parsed_definitions:
                if parsed_definition.get_root_key() == source.from_source:
                    parsed_instance = parsed_definition.instance
                    source_data[parsed_instance] = (parsed_definition.structure)

            if not source_data or len(source_data) == 0:
                return ExecutionResult(plugin_name, "generate", ExecutionStatus.GENERAL_FAILURE, [f"Could not find source data for generator source {source.from_source}"])
            

            # go through each generator template
            for template in source.templates:

                # figure out how to load func_dict into the jinja2 environment
                helper_functions: dict[str, Callable] = {}
                for helper in template.helper_functions:
                    helper_functions[helper.name] = get_callable(helper.package, helper.file, helper.function)

                # generate code using the template and source
                template_abs_path = path.abspath(path.join(generator_file, template.template_file))

                jinja_template = load_template(template_abs_path, helper_functions)
                for source_data_instance, source_data_structure in source_data.items():
                    output = jinja_template.render(source_data_structure)
                    
                    # TODO: write output to files to the traget in the template, respecting the overwrite indicator
                    root_out_dir = code_out_dir
                    if generator.output_target == GeneratorOutputTarget.TEST:
                        root_out_dir = test_out_dir
                    elif generator.output_target == GeneratorOutputTarget.DOC:
                        root_out_dir = doc_out_dir
                    output_file_path = get_output_file_path(root_out_dir, generator, source_data_instance)

                    # render the template and write contents to output_file_path
                    with open(output_file_path, "w") as output_file:
                        if generator.overwrite == OverwriteOption.OVERWRITE:
                            if path.exists(output_file_path):
                                # make a backup first
                                backup_file_path = f"{output_file_path}.generate_backup"
                                with open(backup_file_path, "w") as backup_file:
                                    backup_file.write(output_file.read())
                            output_file.write(output)
                        elif generator.overwrite == OverwriteOption.MERGE:
                            if path.exists(output_file_path):
                                merge_files(output, output_file_path, output_file_path)
                            else:
                                output_file.write(output)
                        else:
                            if not path.exists(output_file_path):
                                output_file.write(output)
                        
                        output_file.close()
    
    return ExecutionResult(plugin_name, "generate", ExecutionStatus.SUCCESS, [])

def get_output_directories(aac_plugin_file: str, code_output: str, test_output: str, doc_output: str, no_prompt: bool) -> tuple[str, str, str]:

    code_out: str = "."
    test_out: str = "."
    doc_out: str = "."
    
    if not code_output or len(code_output) == 0:
        aac_plugin_path = path.abspath(aac_plugin_file)
        if not path.exists(aac_plugin_file):
            raise ExecutionError(f"The provided AaC Plugin file does not exist: {aac_plugin_file}")
        code_out = path.dirname(aac_plugin_path)
    if not test_output or len(test_output) == 0:
        test_out = code_out.replace("src", "tests")
    if not doc_output or len(doc_output) == 0:
        doc_out_out = code_out.replace("src", "docs")

    if not no_prompt:
        print("AaC Gen-Plugin will generate code and tests in the following directories:")
        print(f"   code: {code_out}")
        print(f"   tests: {test_out}")
        print(f"   docs: {doc_out}")
        approval = "first"
        while approval not in ["y", "Y", "yes", "Yes", "YES", "n", "N", "no", "No", "NO"]:
            approval = input("Do you want to continue? (y/n): ")
        if approval in ["y", "Y", "yes", "Yes", "YES"]:
            return (code_out, test_out, doc_out)
        else:
            raise OperationCancelled("User cancelled generate operation.")

    return (code_out, test_out, doc_out)

def get_output_file_path(root_output_directory: str, generator: GeneratorTemplate, source_instance: Any) -> str:
    result = root_output_directory
    if generator.output_path_uses_data_source_package and source_instance.package:
        result = path.join(result, get_path_from_package(source_instance.package))
    file_name = ""
    if generator.output_file_prefix:
        file_name = generator.output_file_prefix
    if source_instance.name:
        file_name = f"{file_name}{source_instance.name}"
    if generator.output_file_suffix:
        file_name = f"{file_name}{generator.output_file_suffix}"
    file_name = f"{file_name}.{generator.output_file_extension}"
    result = path.join(result, file_name)
    return path.abspath(result)

def get_callable(package_name: str, file_name: str, function_name: str) -> Callable:
    module = importlib.import_module(f"{package_name}.{file_name}")
    return getattr(module, function_name)


def load_template(template_abs_path: str, helper_functions: dict[str, Callable] = {}) -> Template:
    env = Environment(loader=FileSystemLoader('/'))
    env.globals.update(helper_functions)
    template = env.get_template(template_abs_path)
    return template

def backup_file(file_path: str):
    backup_file_path = f"{file_path}.generate_backup"
    with open(file_path, "w") as input_file:
        with open(backup_file_path, "w") as backup_file:
            backup_file.write(input_file.read())

def merge_files(template_output: str, existing_file_path: str, output_file_path: str):
    backup_file(existing_file_path)
    if filecmp.cmp(template_output, existing_file_path):
        # The template output is identical to the existing file, so just copy the existing file to the output file
        shutil.copy(existing_file_path, output_file_path)
    else:
        # The template output is different from the existing file, so merge the changes
        with open(template_output, 'r') as template_file, open(existing_file_path, 'r') as existing_file, open(output_file_path, 'w') as output_file:
            template_lines = template_file.readlines()
            existing_lines = existing_file.readlines()
            diff = difflib.unified_diff(existing_lines, template_lines, fromfile=existing_file_path, tofile=output_file_path)
            output_file.writelines(diff)