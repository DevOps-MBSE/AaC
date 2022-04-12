from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_subcomponent_types(definition_under_test: Definition, target_sub_definition: Definition, active_context: LanguageContext) -> ValidatorResult:
    """
    Validate that the subcomponents of the definition are models.

    Args:
        definition_under_test (Definition): The definition that's being validated. (Root validation definitions)
        target_sub_definition (Definition): A definition with applicable validation. ("Validation" definition)
        active_context (LanguageContext): The active context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []

    def validate_model_subcomponents(dict_to_validate: dict) -> list[str]:
        print(dict_to_validate)
        return []

    dicts_to_test = get_substructures_by_type(definition_under_test, target_sub_definition, active_context)
    list(map(validate_model_subcomponents, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
