from typing import Set

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorFindings, ValidatorResult


SPEC_REF_ID_VALIDATOR_NAME = "Referenced IDs exist"

ALL_REQ_IDS: Set[str] = set()


def validate_referenced_ids(
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

    _get_all_requirement_ids(target_schema_definition, language_context)

    for req_ref_dict in get_substructures_by_type(definition_under_test, target_schema_definition, language_context):
        for req_dict in get_substructures_by_type(definition_under_test, target_schema_definition, language_context):
            for id in req_dict["ids"]:
                if id not in ALL_REQ_IDS:
                    findings.add_error_finding(
                        definition_under_test, f"Referenced requirement '{id}' is not defined", SPEC_REF_ID_VALIDATOR_NAME, definition_under_test.get_lexeme_with_value(id)
                    )

    return ValidatorResult([definition_under_test], findings)


def _get_all_requirement_ids(target_schema_definition, language_context):
    if len(ALL_REQ_IDS) == 0:  # don't repeat this for every validator invocation
        requirement_definition = language_context.get_definition_by_name("Requirement")

        spec_roots = language_context.get_definitions_by_root_key("spec")
        for spec in spec_roots:
            for req_dict in get_substructures_by_type(spec, requirement_definition, language_context):
                ALL_REQ_IDS.add(req_dict["id"])
