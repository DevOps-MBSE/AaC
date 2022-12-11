import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Subcomponents are models"


def validate_subcomponent_types(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validate that the subcomponents of the definition are models.

    Args:
        definition_under_test (Definition): The definition that's being validated. (Root validation definitions)
        target_schema_definition (Definition): A definition with applicable validation. ("Validation" definition)
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_model_subcomponents(dict_to_validate: dict):
        subcomponents = dict_to_validate.get("components", [])

        for component in subcomponents:
            component_type = component.get("type")

            if component_type:
                definition = language_context.get_definition_by_name(component_type)

                expected_type = "model"
                actual_type = definition and definition.get_root_key()
                if definition and actual_type != expected_type:
                    incorrect_subcomponent_type = (
                        f"Expected '{expected_type}' as the subcomponent type but found '{component_type}' with type "
                        f"'{actual_type}' in: {dict_to_validate}"
                    )
                    component_type_lexeme = definition_under_test.get_lexeme_with_value(component_type)
                    findings.add_error_finding(
                        target_schema_definition, incorrect_subcomponent_type, PLUGIN_NAME, component_type_lexeme
                    )
                    logging.debug(incorrect_subcomponent_type)
            else:
                component_name = component.get("name")
                component_missing_type = (
                    f"Expected component '{component_name}' to have the field 'type', but was not present. Bad component:"
                    f"{component}"
                )
                component_name_lexeme = definition_under_test.get_lexeme_with_value(component_name)
                findings.add_error_finding(
                    target_schema_definition, component_missing_type, PLUGIN_NAME, component_name_lexeme
                )
                logging.debug(component_missing_type)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_model_subcomponents, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
