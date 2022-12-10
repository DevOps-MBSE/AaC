"""AaC Plugin implementation module for the aac-spec plugin."""

from aac.lang.definitions.collections import convert_parsed_definitions_to_dict_definition, get_models_by_type
from aac.lang.definitions.search import search
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validate import validated_source

plugin_name = "specification"


def spec_validate(architecture_file: str) -> PluginExecutionResult:
    """
    Validate spec traces within the AaC model.

    Args:
        architecture_file (str): The file to validate for spec cross-references.
    """

    def validate():
        with validated_source(architecture_file) as result:
            definitions_dict = convert_parsed_definitions_to_dict_definition(result.definitions)
            is_valid, validation_errors = _run_spec_validation(definitions_dict)

            if is_valid:
                return f"Spec in {architecture_file} is valid"

            errors = "\n".join(validation_errors)
            raise SpecValidationError(f"Spec in {architecture_file} is invalid:\n{errors}")

    with plugin_result(plugin_name, validate) as result:
        return result


def _run_spec_validation(parsed_model: dict):
    is_valid = True
    validation_errors = []

    # go through the parsed model to find requirement references
    requirement_refs = {}
    for model_name in parsed_model:
        refs = []
        refs.extend(search(parsed_model[model_name], ["spec", "requirements", "parent", "ids"]))
        refs.extend(search(parsed_model[model_name], ["model", "behavior", "requirements", "ids"]))
        refs.extend(search(parsed_model[model_name], ["schema", "requirements", "ids"]))
        if refs:
            requirement_refs[model_name] = refs

    specs = get_models_by_type(parsed_model, "spec")
    requirements_by_id = _collect_ids_from_specs(specs)

    # ensure all req_refs are present in the referenced location
    for model_name, id_references in requirement_refs.items():

        # Check the refs exists
        defined_requirement_ids = list(requirements_by_id.keys())
        for requirement_id in id_references:
            if requirement_id not in defined_requirement_ids:
                is_valid = False
                validation_errors.append(
                    f"Invalid requirement id '{requirement_id}' reference in '{model_name}':  {defined_requirement_ids}"
                )

    return is_valid, validation_errors


def _collect_ids_from_specs(specs: list[dict]) -> dict:
    """Return all ids and their definitions as a key-value pair with the id being the key."""
    requirements_by_id = {}

    for spec in specs.values():
        spec_definition = spec.get("spec")
        spec_requirements = spec_definition.get("requirements") or []
        spec_sections = spec_definition.get("sections") or []

        for requirement in spec_requirements:
            requirements_by_id[requirement.get("id")] = requirement

        for section in spec_sections:
            section_requirements = section.get("requirements")

            for section_requirement in section_requirements:
                requirements_by_id[section_requirement.get("id")] = section_requirement

    return requirements_by_id


class SpecValidationError(PluginError):
    """An error related to spec validation."""

    pass
