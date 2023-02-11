"""AaC validator implementation module for specification req reference ids."""
from typing import Set, Dict, List

import traceback
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorFindings, ValidatorResult
from aac.plugins.first_party.material_model.material_model_impl import plugin_name


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
            for part_ref_dict in get_substructures_by_type(root, part_ref_definition, language_context):
                if part_ref_dict:
                    part_ref = part_ref_dict["part-ref"]
                    if not _definition_name_exists(part_ref, ALL_PART_NAMES):

                        lexeme = root.get_lexeme_with_value(part_ref)
                        message = f"Cannot find referenced part {part_ref} in {lexeme.source} on line {lexeme.location.line + 1}"

                        findings.add_error_finding(definition_under_test, message, MATERIAL_REF_VALIDATOR_NAME, lexeme)
                        logging.debug(message)

            # check assembly refs
            for assembly_ref_dict in get_substructures_by_type(root, assembly_ref_definition, language_context):
                if assembly_ref_dict:
                    assembly_ref = assembly_ref_dict["assembly-ref"]
                    if not _definition_name_exists(assembly_ref, ALL_ASSEMBLY_NAMES):

                        lexeme = root.get_lexeme_with_value(assembly_ref)
                        message = f"Cannot find referenced assembly {assembly_ref} in {lexeme.source} on line {lexeme.location.line + 1}"

                        findings.add_error_finding(definition_under_test, message, MATERIAL_REF_VALIDATOR_NAME, lexeme)
                        logging.debug(message)

            # check deployment refs
            for deployment_ref_dict in get_substructures_by_type(root, deployment_ref_definition, language_context):
                if deployment_ref_dict:
                    deployment_ref = deployment_ref_dict["deployment-ref"]
                    if not _definition_name_exists(deployment_ref, ALL_DEPLOYMENT_NAMES):

                        lexeme = root.get_lexeme_with_value(deployment_ref)
                        message = f"Cannot find referenced deployment {deployment_ref} in {lexeme.source} on line {lexeme.location.line + 1}"

                        findings.add_error_finding(definition_under_test, message, MATERIAL_REF_VALIDATOR_NAME, lexeme)
                        logging.debug(message)

    except Exception as e:
        print("Caught an exception in validate_referenced_materials")
        print(e)
        print(traceback.format_exc())

    return ValidatorResult([definition_under_test], findings)


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
