import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_subcomponent_types(definition_under_test: Definition, target_schema_definition: Definition, active_context: LanguageContext) -> ValidatorResult:
    """
    Validate that the subcomponents of the definition are models.

    Args:
        definition_under_test (Definition): The definition that's being validated. (Root validation definitions)
        target_schema_definition (Definition): A definition with applicable validation. ("Validation" definition)
        active_context (LanguageContext): The active context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []

    def validate_model_subcomponents(dict_to_validate: dict):
        subcomponents = dict_to_validate.get("components", [])

        for component in subcomponents:
            component_type = component.get("type")
            definition = active_context.get_definition_by_name(component_type)

            expected_type = "model"
            actual_type = definition and definition.get_root_key()
            if definition and actual_type != expected_type:
                incorrect_subcomponent_type = (
                    f"Expected '{expected_type}' as the subcomponent type but found '{component_type}' with type "
                    f"'{actual_type}' in: {dict_to_validate}"
                )
                error_messages.append(incorrect_subcomponent_type)
                logging.debug(incorrect_subcomponent_type)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, active_context)
    list(map(validate_model_subcomponents, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
