import logging
from typing import Optional

from aac.lang.language_context import LanguageContext
from aac.lang.constants import DEFINITION_FIELD_NAME, DEFINITION_FIELD_VALIDATION, ROOT_KEY_SCHEMA
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.lang.definitions.schema import get_definition_schema_components
from aac.lang.hierarchy import get_definition_ancestry
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution


def get_applicable_validators_for_definition(
    definition: Definition, validator_plugins: list[DefinitionValidationContribution], context: LanguageContext
) -> list[DefinitionValidationContribution]:
    """
    Return a list of all validator plugins that are applicable to the definition.

    Args:
        definition (Definition): The definition to search through.
        validator_plugins (list[DefinitionValidationContribution]): The list of available, registered validator plugins.
        context (LanguageContext): The language context

    Returns:
        A list of validator plugins that can be applied to the definition.

        The validator plugins are deemed applicable if the definition contains fields or substructures that
        are validated, such as field references.
    """

    ancestor_definitions = get_definition_ancestry(definition, context)
    sub_structure_definitions = get_definition_schema_components(definition, context)
    # For each ancestor definition, pull validation definitions, collapse the 2d list to 1d, and return the list of validations.
    ancestor_lists = map(_get_validation_entries, ancestor_definitions)
    substructure_lists = map(_get_validation_entries, sub_structure_definitions)

    applicable_ancestor_validation_dicts = [ancestor for ancestor_list in ancestor_lists for ancestor in ancestor_list]
    applicable_substructure_validation_dicts = [substructure for substructure_list in substructure_lists for substructure in substructure_list]
    applicable_validation_dicts = applicable_ancestor_validation_dicts + applicable_substructure_validation_dicts

    applicable_validators = {}
    for validation_dict in applicable_validation_dicts:
        validation_name = validation_dict.get(DEFINITION_FIELD_NAME)
        validator_plugin = _get_validator_plugin_by_name(validation_name, validator_plugins)

        if validator_plugin:
            applicable_validators[validation_name] = validator_plugin
        else:
            logging.error(
                f"Failed to find applicable validator plugin for name '{validation_name}' out of the available plugins:\n{applicable_validation_dicts}"
            )

    return list(applicable_validators.values())


def _get_validation_entries(definition: Definition) -> list[dict]:
    """Return a list of validation entries from the definition."""

    validations = {}

    # Currently validations are only registered in `data` root definitions.
    if definition.get_root_key() == ROOT_KEY_SCHEMA:
        validations = search_definition(definition, [ROOT_KEY_SCHEMA, DEFINITION_FIELD_VALIDATION])

    return validations


def _get_validator_plugin_by_name(validator_name: str, validator_plugins: list[DefinitionValidationContribution]) -> Optional[DefinitionValidationContribution]:
    filtered_validators = list(filter(lambda plugin: plugin.name == validator_name, validator_plugins))
    filtered_validators_count = len(filtered_validators)

    validator_plugin = None
    if filtered_validators_count > 1:
        logging.error(
            f"Found multiple plugins with the same name '{validator_name}' in registered plugins:\n{validator_plugins}"
        )
    elif filtered_validators_count < 1:
        logging.error(
            f"Failed to find validator plugin by name '{validator_name}' in registered plugins:\n{validator_plugins}"
        )
    else:
        validator_plugin = filtered_validators[0]

    return validator_plugin
