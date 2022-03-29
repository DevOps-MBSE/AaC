import logging
from typing import Optional
from iteration_utilities import flatten

from aac.lang.definition_helpers import get_definition_by_name, search_definition, remove_list_type_indicator
from aac.lang.hierarchy import get_definition_ancestry
from aac.parser import ParsedDefinition
from aac.plugins.validators import ValidatorPlugin
from aac.lang import ActiveContext


def get_applicable_validators_for_definition(
    definition: ParsedDefinition, validator_plugins: list[ValidatorPlugin], context: ActiveContext
) -> list[ValidatorPlugin]:
    """Traverse the definition and identify all applicable validator plugins."""

    ancestor_definitions = get_definition_ancestry(definition, context)
    # For each ancestor definition, pull validation definitions, collapse the 2d list to 1d, and return the list of validations.
    applicable_ancestor_validation_dicts = list(flatten(map(_get_validation_entries, ancestor_definitions)))
    applicable_substructure_validation_dicts = _get_validation_entries_from_definition_fields(definition, context)
    applicable_validation_dicts = applicable_ancestor_validation_dicts + applicable_substructure_validation_dicts

    applicable_validators = {}
    for validation_dict in applicable_validation_dicts:
        validation_name = validation_dict.get("name")
        validator_plugin = _get_validator_plugin_by_name(validation_name, validator_plugins)

        if validator_plugin:
            applicable_validators[validation_name] = validator_plugin
        else:
            logging.error(
                f"Failed to find applicable validator plugin for name '{validation_name}' out of the available plugins:\n{applicable_validation_dicts}"
            )

    return list(applicable_validators.values())


def _get_validation_entries_from_definition_fields(definition: ParsedDefinition, context: ActiveContext) -> list[dict]:
    """Return a list of validation entries from substructures and fields in the definition."""

    def _recursively_gather_field_validations(field_definition: ParsedDefinition, traversed_types: list[str]) -> list[dict[str, list]]:
        validations = {}
        definition_root_key = field_definition.get_root_key()
        traversed_types.append(field_definition.name)
        definition_root_structure = get_definition_by_name(definition_root_key, context.context_definitions)
        definition_field_structures_dict = search_definition(
            definition_root_structure, [definition_root_structure.get_root_key(), "fields"]
        )

        for field in definition_field_structures_dict:
            field_type = remove_list_type_indicator(field.get("type"))

            if field_type in traversed_types:
                continue

            # Since enums don't support the validation field, we can ignore primitive types
            if context.is_definition_type(field_type):
                type_definition = get_definition_by_name(field_type, context.context_definitions)
                field_type_validations = _get_validation_entries(type_definition)
                if len(field_type_validations) > 0:
                    validations[field_type] = field_type_validations

                validations = validations | _recursively_gather_field_validations(type_definition, traversed_types)

        return validations

    validations = flatten(_recursively_gather_field_validations(definition, []).values())
    return list(validations)


def _get_validation_entries(definition: ParsedDefinition) -> list[dict]:
    """Return a list of validation entries from the definition."""

    validations = {}

    # Currently validations are only registered in `data` root definitions.
    if definition.get_root_key() == "data":
        validations = search_definition(definition, ["data", "validation"])

    return validations


def _get_validator_plugin_by_name(validator_name: str, validator_plugins: list[ValidatorPlugin]) -> Optional[ValidatorPlugin]:
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
