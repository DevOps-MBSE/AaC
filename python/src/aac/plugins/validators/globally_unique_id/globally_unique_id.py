from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.definitions.search import search
from aac.plugins.validators import ValidatorFindings, ValidatorResult


UNIQUE_REQ_ID_VALIDATOR_NAME = "Requirement id is unique"


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

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    if dicts_to_test:
        
        spec_roots = language_context.get_definitions_by_root_key("spec")
        global_ids = set()
        for spec in spec_roots:
            for id in search(spec.structure, ["spec", "requirements", "id"]):
                if id in global_ids:
                    findings.add_error_finding(
                        definition_under_test, f"{id} is not a unique requirement id", UNIQUE_REQ_ID_VALIDATOR_NAME, definition_under_test.get_lexeme_with_value("id")
                    )
                else:
                    global_ids.add(id)

    return ValidatorResult([definition_under_test], findings)
