"""Module for features and functionality for Schema inheritance."""
from typing import Optional

from aac.lang.constants import DEFINITION_FIELD_FIELDS, DEFINITION_FIELD_VALIDATION
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext


def get_inherited_attributes(definition: Definition, language_context: LanguageContext) -> Optional[dict[str, dict]]:
    """
    Returns a dictionary of parent definition to transitive attributes. Each dictionary value is another dictionary of the transitive fields.

    Args:
        definition (Definition): The definition to search for inherited superclass definitions.
        language_context (LanguageContext): The LanguageContext to lookup inherited definitions from.

    Returns:
        A dictionary of parent-definition name to transitive fields. If the inherits field is not present, return None.
    """
    transitive_parent_attributes = None

    inherited_definition_names = definition.get_inherits()
    if inherited_definition_names:
        transitive_parent_attributes = {}

        for inherited_definition_name in inherited_definition_names:
            inherited_definition = language_context.get_definition_by_name(inherited_definition_name)

            if inherited_definition:
                transitive_fields = inherited_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
                transitive_validation = inherited_definition.get_validations()
                transitive_parent_attributes[inherited_definition.name] = {
                    DEFINITION_FIELD_FIELDS: transitive_fields,
                    DEFINITION_FIELD_VALIDATION: transitive_validation,
                }

    return transitive_parent_attributes


def apply_inherited_attributes_to_definition(definition: Definition, language_context: LanguageContext) -> None:
    """
    Retrieves the inherited attributes and applies them to the definition.

    Args:
        definition (Definition): The definition to search for inherited superclass definitions.
        language_context (LanguageContext): The LanguageContext to lookup inherited definitions from.

    Returns:
        None. The definition's structure is altered in place.
    """
    transitive_parent_attributes = get_inherited_attributes(definition, language_context)

    if transitive_parent_attributes:
        for definition_name in transitive_parent_attributes:
            attributes_to_apply = transitive_parent_attributes.get(definition_name, {})
            fields_to_apply = attributes_to_apply.get(DEFINITION_FIELD_FIELDS) or []
            validation_to_apply = attributes_to_apply.get(DEFINITION_FIELD_VALIDATION) or []
            existing_fields = definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS) or []
            existing_validation = definition.get_top_level_fields().get(DEFINITION_FIELD_VALIDATION) or []

            definition.get_top_level_fields()[DEFINITION_FIELD_FIELDS] = existing_fields + fields_to_apply
            definition.get_top_level_fields()[DEFINITION_FIELD_VALIDATION] = existing_validation + validation_to_apply
