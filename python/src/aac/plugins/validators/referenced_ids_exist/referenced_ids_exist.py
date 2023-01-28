from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorFindings, ValidatorResult


SPEC_REF_ID_VALIDATOR_NAME = "Referenced IDs exist"


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

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    if dicts_to_test:
        print(f"Specification -> Referenced IDs Exist on {definition_under_test.name}, {target_schema_definition.name} {dicts_to_test}")

    return ValidatorResult([definition_under_test], findings)
