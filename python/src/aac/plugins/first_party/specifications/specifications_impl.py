"""AaC Plugin implementation module for the aac-spec plugin."""
import csv
from os import path, makedirs
from typing import List

from aac.lang.definitions.definition import Definition
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validate import validated_source

plugin_name = "specification"


def spec_csv(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Generate a csv requirements table from a specification definition.

    Args:
        architecture_file (str): The file to process for spec content.

        output_directory (str): The directory to write csv spec content.
    """

    def get_csv():
        spec_definitions = _get_parsed_models(architecture_file)
        reqs = {}
        for spec in spec_definitions:
            reqs[spec.name] = _get_requirements(spec)

        field_names = ["Spec Name", "Section", "ID", "Requirement", "Parents", "Children"]

        # just in case, let's make sure the output directory exists
        if not path.lexists(output_directory):
            makedirs(output_directory)

        file_counter = 0
        for spec_name in reqs.keys():
            file_name = spec_name + ".csv"
            file_name = file_name.replace(" ", "_")
            output_path = path.join(output_directory, file_name)
            with open(output_path, 'w') as output:
                writer = csv.DictWriter(output, fieldnames=field_names)
                writer.writeheader()
                writer.writerows(reqs[spec_name])
                file_counter = file_counter + 1

        return f"{file_counter} CSV spec files written to {output_directory}"

    with plugin_result(plugin_name, get_csv) as result:
        return result


def _get_parsed_models(architecture_file: str) -> List[Definition]:
    with validated_source(architecture_file) as result:
        return result.definitions


def _get_requirements(spec: Definition) -> List[dict]:
    ret_val: List[dict] = []
    if spec.get_root_key() in ["spec"]:  # make sure we're actually working with a spec here
        # collect data
        spec_dict: dict = spec.structure
        spec_name = spec_dict["spec"]["name"]

        # handle the spec root requirements
        for req in spec_dict["spec"]["requirements"]:
            ret_val.append(_gen_spec_line_from_req_dict(spec_name, "", req))

        # handle the requirements in each section
        if "sections" in spec_dict["spec"].keys():
            for section in spec_dict["spec"]["sections"]:
                section_name = section["name"]
                for req in section["requirements"]:
                    ret_val.append(_gen_spec_line_from_req_dict(spec_name, section_name, req))
    return ret_val


def _gen_spec_line_from_req_dict(spec_name: str, section_name: str, req: dict) -> dict:
    line = {}
    line["Spec Name"] = spec_name
    line["Section"] = section_name
    line["ID"] = req["id"]
    line["Requirement"] = req["shall"]
    parent_ids = ""
    if "parent" in req.keys():
        for parent_id in req["parent"]["ids"]:
            if len(parent_ids) == 0:
                parent_ids = f"{parent_id}"
            else:
                parent_ids = f"{parent_ids} {parent_id}"
        line["Parents"] = parent_ids
    child_ids = ""
    if "child" in req.keys():
        for child_id in req["child"]["ids"]:
            if len(child_ids) == 0:
                child_ids = f"{child_id}"
            else:
                child_ids = f"{child_ids} {child_id}"
    line["Children"] = child_ids
    return line
