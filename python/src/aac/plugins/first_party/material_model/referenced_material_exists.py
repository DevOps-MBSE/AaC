"""AaC validator implementation module for specification req reference ids."""
import traceback
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorFindings, ValidatorResult


MATERIAL_REF_VALIDATOR_NAME = "Referenced materials exist"

ALL_PART_NAMES = []
ALL_ASSEMBLY_NAMES = []
ALL_DEPLOYMENT_NAMES = []


def validate_referenced_materials(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the referenced requirement id exists within the context.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    # this feels like a hack, but it does prevent the validator from repeatedly running on the same data sets
    if len(ALL_PART_NAMES) + len(ALL_ASSEMBLY_NAMES) + len(ALL_DEPLOYMENT_NAMES) > 0:
        return ValidatorResult([definition_under_test], findings)

    try:

        _get_all_material_names(language_context)

        part_ref_definition = language_context.get_definition_by_name("PartRef")
        assembly_ref_definition = language_context.get_definition_by_name("AssemblyRef")
        deployment_ref_definition = language_context.get_definition_by_name("DeploymentRef")

        assembly_roots = language_context.get_definitions_by_root_key("assembly")
        deployment_roots = language_context.get_definitions_by_root_key("deployment")
        for root in assembly_roots + deployment_roots:

            # check part refs
            _check_refs("part-ref", ALL_PART_NAMES, root, definition_under_test, part_ref_definition, language_context, findings)

            # check assembly refs
            _check_refs("assembly-ref", ALL_ASSEMBLY_NAMES, root, definition_under_test, assembly_ref_definition, language_context, findings)

            # check deployment refs
            _check_refs("deployment-ref", ALL_DEPLOYMENT_NAMES, root, definition_under_test, deployment_ref_definition, language_context, findings)

    except Exception as e:
        print("Caught an exception in validate_referenced_materials")
        print(e)
        print(traceback.format_exc())

    return ValidatorResult([definition_under_test], findings)


def _check_refs(ref_type, name_list, root, definition_under_test, ref_definition, language_context, findings):
    for ref_dict in get_substructures_by_type(root, ref_definition, language_context):
        if ref_dict:
            ref = ref_dict[ref_type]
            if not _definition_name_exists(ref, name_list):

                lexeme = root.get_lexeme_with_value(ref)
                message = f"Cannot find {ref_type} target {ref} in {lexeme.source} on line {lexeme.location.line + 1}"

                findings.add_error_finding(definition_under_test, message, MATERIAL_REF_VALIDATOR_NAME, lexeme)
                logging.debug(message)


def _get_all_material_names(language_context):
    if len(ALL_PART_NAMES) == 0:  # don't repeat this for every validator invocation
        part_roots = language_context.get_definitions_by_root_key("part")
        for part in part_roots:
            ALL_PART_NAMES.append(part.name)

    if len(ALL_ASSEMBLY_NAMES) == 0:  # don't repeat this for every validator invocation
        assembly_roots = language_context.get_definitions_by_root_key("assembly")
        for assembly in assembly_roots:
            ALL_ASSEMBLY_NAMES.append(assembly.name)

    if len(ALL_DEPLOYMENT_NAMES) == 0:  # don't repeat this for every validator invocation
        deployment_roots = language_context.get_definitions_by_root_key("deployment")
        for deployment in deployment_roots:
            ALL_DEPLOYMENT_NAMES.append(deployment.name)


def _definition_name_exists(name, definition_list):
    return name in definition_list
