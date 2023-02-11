"""AaC validator implementation module for specification req reference ids."""
import traceback
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


CIRCULAR_REF_VALIDATOR_NAME = "No circular material references"

deployment_tree = {}
assembly_tree = {}


def validate_no_circluar_material_refs(
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

    try:

        if len(assembly_tree.keys()) + len(deployment_tree.keys()) > 0:
            # already done, so skip
            return ValidatorResult([definition_under_test], findings)
        else:

            _get_deployment_tree(language_context)
            _get_assembly_tree(language_context)

            # check deployments for cycles
            deployment_roots = language_context.get_definitions_by_root_key("deployment")
            for root in deployment_roots:

                dupe = _look_for_dupes(root.name, [], deployment_tree)
                if dupe:
                    lexeme = root.get_lexeme_with_value(dupe)
                    message = f"Circular deployment reference detected for {dupe} in {lexeme.source} on line {lexeme.location.line + 1}"

                    findings.add_error_finding(definition_under_test, message, CIRCULAR_REF_VALIDATOR_NAME, lexeme)
                    logging.debug(message)

            # check assemblies for cycles
            assembly_roots = language_context.get_definitions_by_root_key("assembly")
            for root in assembly_roots:

                dupe = _look_for_dupes(root.name, [], assembly_tree)
                if dupe:
                    lexeme = root.get_lexeme_with_value(dupe)
                    message = f"Circular assembly reference detected for {dupe} in {lexeme.source} on line {lexeme.location.line + 1}"

                    findings.add_error_finding(definition_under_test, message, CIRCULAR_REF_VALIDATOR_NAME, lexeme)
                    logging.debug(message)

    except Exception as e:
        print("Caught an exception in validate_no_circluar_material_refs")
        print(e)
        print(traceback.format_exc())

    return ValidatorResult([definition_under_test], findings)


def _look_for_dupes(key, visited, pool):
    """Return duplicate name if found, otherwise None."""
    if key in visited:
        return key

    history = visited.copy()
    history.append(key)
    for value in pool[key]:
        return _look_for_dupes(value, history, pool)

    return None


def _get_deployment_tree(language_context):

    deployment_roots = language_context.get_definitions_by_root_key("deployment")
    for deployment in deployment_roots:
        if "sub-deployments" in deployment.structure["deployment"].keys():
            subs = []
            for sub in deployment.structure["deployment"]["sub-deployments"]:
                subs.append(sub["deployment-ref"])
            deployment_tree[deployment.name] = subs

        else:
            deployment_tree[deployment.name] = []


def _get_assembly_tree(language_context):

    assembly_roots = language_context.get_definitions_by_root_key("assembly")
    for assembly in assembly_roots:
        if "sub-assemblies" in assembly.structure["assembly"].keys():
            subs = []
            for sub in assembly.structure["assembly"]["sub-assemblies"]:
                subs.append(sub["assembly-ref"])
            assembly_tree[assembly.name] = subs

        else:
            assembly_tree[assembly.name] = []
