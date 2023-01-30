"""AaC validator implementation module for specification global req id uniqueness."""
from typing import Tuple, Set, Dict

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorFindings, ValidatorResult


UNIQUE_REQ_ID_VALIDATOR_NAME = "Requirement id is unique"

# this has to be global so that it persists across validator invocations on each definition
ERROR_MSGS = set()


def validate_unique_ids(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the id of a Requirement is globally unique within the context.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    # this test must be performed globally
    global_ids: Dict[str, Definition] = {}
    spec_roots = language_context.get_definitions_by_root_key("spec")
    for spec in spec_roots:
        unique_ids, duplicate_ids = _test_spec_ids(spec, target_schema_definition, language_context)
        if len(duplicate_ids) > 0:
            for id in duplicate_ids:
                if spec.get_lexeme_with_value(id):  # have to do this because you sometimes get duplicate ids form imported specs
                    findings.add_error_finding(
                        spec, f"{id} is not a unique requirement id within spec {spec.name}", UNIQUE_REQ_ID_VALIDATOR_NAME, spec.get_lexeme_with_value(id)
                    )
        for id in unique_ids:
            if id in global_ids:
                # found a cross definition duplicate
                msg = f"{id} is not a unique requirement across specs '{spec.name}' and '{global_ids[id].name}'"
                if msg not in ERROR_MSGS:  # if we don't do this check we'll get the same findings multiple times
                    ERROR_MSGS.add(msg)
                    # issue two findings, one for each file
                    findings.add_error_finding(spec, msg, UNIQUE_REQ_ID_VALIDATOR_NAME, spec.get_lexeme_with_value(id))
                    findings.add_error_finding(global_ids[id], msg, UNIQUE_REQ_ID_VALIDATOR_NAME, global_ids[id].get_lexeme_with_value(id))
            else:
                global_ids[id] = spec

    return ValidatorResult([definition_under_test], findings)


def _test_spec_ids(spec_definition: Definition, requirement_definition: Definition, language_context: LanguageContext) -> Tuple[Set, Set]:
    """
    Searches a given spec definition for duplicate ids.

    Args:
        spec_definition (Definition): The definition that's being validated.
        requirements_definition (Definition): A definition for the Requirement type.
        language_context (LanguageContext): The language context.

    Returns:
        A set of discovered local requirement ids and a set of duplicate ids within the definition.
    """
    local_ids = set()
    duplicate_ids = set()

    for req_dict in get_substructures_by_type(spec_definition, requirement_definition, language_context):
        id = req_dict["id"]
        if id in local_ids:
            duplicate_ids.add(id)
        else:
            local_ids.add(id)

    return local_ids, duplicate_ids
