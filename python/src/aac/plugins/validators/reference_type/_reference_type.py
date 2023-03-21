from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Reference is type"


def validate_reference_types(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
    **validation_kw_args,
) -> ValidatorResult:
    """
    Validate that fields listed in the arguments reference definitions with a root key matching the field's corresponding value.

    Args:
        definition_under_test (Definition): The definition that's being validated. (Root validation definitions)
        target_schema_definition (Definition): A definition with applicable validation. ("Validation" definition)
        language_context (LanguageContext): The language context.
        validation_kw_args (dict[str, str]): A key-value pair where the key is the field name to validate and the value the type constraint

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_reference_type(dict_to_validate: dict):

        for field_name, field_type in validation_kw_args.items():

            field_value_to_test = dict_to_validate.get(field_name, "")

            root_keys = language_context.get_root_keys()
            referenced_definition = language_context.get_definition_by_name(field_value_to_test)

            if not referenced_definition:
                missing_reference = (
                    f"Can't find the referenced definition '{field_value_to_test}' in the context. "
                )
                reference_lexeme = definition_under_test.get_lexeme_with_value(field_value_to_test)
                findings.add_error_finding(
                    definition_under_test, missing_reference, PLUGIN_NAME, reference_lexeme
                )

            elif field_type not in root_keys:
                bad_constraint_type = (
                    f"Expected '{field_type}' to be a root key, but it wasn't found in the current keys: {root_keys}"
                )
                reference_lexeme = target_schema_definition.get_lexeme_with_value(field_type)
                findings.add_warning_finding(
                    definition_under_test, bad_constraint_type, PLUGIN_NAME, reference_lexeme
                )

            elif referenced_definition.get_root_key() != field_type:
                incorrect_reference_type = (
                    f"Expected the referenced definition '{referenced_definition.name}' to have the root key '{field_type}'."
                )
                reference_lexeme = definition_under_test.get_lexeme_with_value(field_value_to_test)
                findings.add_error_finding(
                    definition_under_test, incorrect_reference_type, PLUGIN_NAME, reference_lexeme
                )

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_reference_type, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
