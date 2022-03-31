import logging
from typing import Optional
from iteration_utilities import flatten

from aac.lang.definition_helpers import (
    search_definition,
    get_definition_fields_and_types,
)
from aac.lang.hierarchy import get_definition_ancestry
from aac.lang.definitions.definition import Definition
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.lang.context import LanguageContext


def validate_definition(
    definition: Definition, validator_plugins: list[ValidatorPlugin], context: LanguageContext
) -> list[ValidatorResult]:
    """Traverse the definition validate it."""

    validator_results = []
    ancestor_definitions = get_definition_ancestry(definition, context)

    # For each ancestor definition, get validation definitions, collapse the 2d list to 1d, and return the list of validations.
    applicable_ancestor_validation_dicts = list(flatten(map(_get_validation_entries, ancestor_definitions)))

    # Ancestor validators apply to the whole definition structure
    for validation_dict in applicable_ancestor_validation_dicts:
        validation_name = validation_dict.get("name")
        validator_plugin = _get_validator_plugin_by_name(validation_name, validator_plugins)

        if validator_plugin:
            validator_results.append(_apply_validator(validation_dict, validator_plugin))

    # Traverse through the definition and validate its fields and sub-structures.
    validator_results.extend(_validate_definition_substructure(definition, validator_plugins, context))

    return validator_results


def _validate_definition_substructure(
    definition: Definition, validator_plugins: list[ValidatorPlugin], context: LanguageContext
) -> list[ValidatorResult]:
    """Return a list of validator results from recursively validating the populated fields of the definition."""
    validator_results = []

    def _apply_validation(content_to_validate: dict, validators: list[ValidatorPlugin]) -> list[ValidatorResult]:
        validator_results.extend(
            [_apply_validator(content_to_validate, context, validator) for validator in validators]
        )

    def _recursively_apply_field_validations(definition_to_validate: Definition) -> None:
        """Recurse through the fields and identify validations to apply."""
        definition_fields_dict = get_definition_fields_and_types(definition_to_validate, context.definitions)

        for field_name, field_definition in definition_fields_dict.items():
            fields_to_validate = search_definition(definition_to_validate, [definition_to_validate.get_root_key(), field_name])

            # Skip empty fields, primitive types, self-defining endless loops
            if (
                not fields_to_validate
                or not hasattr(field_definition, "name")
                or definition_to_validate.name == field_definition.name
            ):
                continue

            field_type_validations = _get_validation_entries(field_definition)
            applicable_validators = [
                _get_validator_plugin_by_name(validation.get("name"), validator_plugins)
                for validation in field_type_validations
            ]

            # If the field is not an array type
            if isinstance(fields_to_validate, dict):
                _apply_validation(fields_to_validate, applicable_validators)
                # Need to recurse here for embedded definitions

            # Else if the field is an array type
            elif isinstance(fields_to_validate, list):
                for field_to_validate in fields_to_validate:
                    _apply_validation(field_to_validate, applicable_validators)
                    # Need to recurse here for embedded definitions

    # Pre-populate with the root key a being traversed since we have already validate the root structure
    _recursively_apply_field_validations(definition)
    return validator_results


def _get_validation_entries(definition: Definition) -> list[dict]:
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


def _apply_validator(
    definition_structure_dict: dict, context: LanguageContext, validator_plugin: ValidatorPlugin
) -> ValidatorResult:
    """Executes the validator callback on the applicable dictionary structure or substructure."""
    return validator_plugin.validation_function(definition_structure_dict, context, **validator_plugin.arguments)
