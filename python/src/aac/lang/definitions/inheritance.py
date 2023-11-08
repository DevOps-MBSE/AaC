"""Module for features and functionality for Schema inheritance."""
from typing import Optional

from aac.lang.constants import DEFINITION_FIELD_FIELDS, DEFINITION_FIELD_VALIDATION
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext


def get_inherited_attributes(definition: Definition, language_context: LanguageContext) -> Optional[dict[str, dict]]:   #POPO update
    """
    Returns a dictionary of parent definition to transitive attributes. Each dictionary value is another dictionary of the transitive fields.

    Args:
        definition (Definition): The definition to search for inherited superclass definitions.
        language_context (LanguageContext): The LanguageContext to lookup inherited definitions from.

    Returns:
        A dictionary of parent-definition name to transitive fields. If the inherits field is not present, return None.
    """
    transitive_parent_attributes = None

    inherited_definition_names = definition.get_inherits()  #POPO update
    if inherited_definition_names:  #POPO update
        transitive_parent_attributes = {}

        for inherited_definition_name in inherited_definition_names:    #POPO update
            inherited_definition = language_context.get_definition_by_name(inherited_definition_name)   #POPO update

            if inherited_definition:    #POPO update
                transitive_fields = inherited_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS)    #POPO update
                transitive_validation = inherited_definition.get_validations()  #POPO update
                transitive_parent_attributes[inherited_definition.name] = {   #POPO update
                    DEFINITION_FIELD_FIELDS: transitive_fields,   #POPO update
                    DEFINITION_FIELD_VALIDATION: transitive_validation,   #POPO update
                }

    return transitive_parent_attributes


def apply_inherited_attributes_to_definition(definition: Definition, language_context: LanguageContext) -> None:    #POPO update
    """
    Retrieves the inherited attributes and applies them to the definition.

    Args:
        definition (Definition): The definition to search for inherited superclass definitions.
        language_context (LanguageContext): The LanguageContext to lookup inherited definitions from.

    Returns:
        None. The definition's structure is altered in place.
    """
    transitive_parent_attributes = get_inherited_attributes(definition, language_context)   #POPO update

    if transitive_parent_attributes:    
        for definition_name in transitive_parent_attributes:    #POPO update
            attributes_to_apply = transitive_parent_attributes.get(definition_name, {})   #POPO update
            fields_to_apply = attributes_to_apply.get(DEFINITION_FIELD_FIELDS) or []    #POPO update
            validation_to_apply = attributes_to_apply.get(DEFINITION_FIELD_VALIDATION) or []    #POPO update
            existing_fields = definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS) or []  #POPO update
            existing_validation = definition.get_top_level_fields().get(DEFINITION_FIELD_VALIDATION) or []  #POPO update

            definition.get_top_level_fields()[DEFINITION_FIELD_FIELDS] = existing_fields + fields_to_apply  #POPO update
            definition.get_top_level_fields()[DEFINITION_FIELD_VALIDATION] = existing_validation + validation_to_apply  #POPO update
