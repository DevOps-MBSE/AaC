from contextlib import contextmanager
from iteration_utilities import flatten
from typing import Generator

from aac.lang.language_context import LanguageContext
from aac.lang.language_error import LanguageError
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema_components
from aac.lang.hierarchy import get_definition_ancestry
from aac.io.parser import parse
from aac.plugins.plugin_manager import get_validator_plugins
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.validate._validation_error import ValidationError
from aac.validate._validation_result import ValidationResult
from aac.validate._collect_validators import get_applicable_validators_for_definition


@contextmanager
def validated_definitions(user_definitions: list[Definition]) -> Generator[ValidationResult, None, None]:
    """Validate user-defined definitions along with the definitions in the ActiveContext.

    Args:
        user_definitions (list[Definition]): A list of user-defined definitions to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation(user_definitions)


@contextmanager
def validated_source(source: str) -> Generator[ValidationResult, None, None]:
    """Run validation on a string-based YAML definition or a YAML file.

    Args:
        source (str): The source of the YAML representation of the model.

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation(parse(source))


def _with_validation(user_definitions: list[Definition]) -> ValidationResult:
    result = _validate_definitions(user_definitions)
    try:
        if result.is_valid:
            return result
        else:
            raise ValidationError("Failed to validate content with errors:", *result.messages)
    except LanguageError as error:
        raise ValidationError("Failed to validate content due to an internal language error:\n", *error.args)


def _validate_definitions(user_definitions: list[Definition]) -> ValidationResult:
    registered_validators = get_validator_plugins()
    active_context = get_active_context()
    active_context.add_definitions_to_context(user_definitions)

    def validate_each_definition(definition: Definition) -> list[ValidatorResult]:
        return _validate_definition(definition, registered_validators, active_context)

    validator_results = list(flatten(map(validate_each_definition, active_context.definitions)))
    validator_messages = []
    invalid_results = []

    for result in validator_results:
        validator_messages.extend(result.messages)
        if not result.is_valid:
            invalid_results.extend(result.messages)

    return ValidationResult(user_definitions, validator_messages, (len(invalid_results) < 1))


def _validate_definition(
    definition: Definition, validator_plugins: list[ValidatorPlugin], context: LanguageContext
) -> list[ValidatorResult]:
    """Traverse the definition and validate it according to the validator plugins."""

    validator_results = []

    applicable_validator_plugins = get_applicable_validators_for_definition(definition, validator_plugins, context)
    ancestor_definitions = get_definition_ancestry(definition, context)
    sub_structure_definitions = get_definition_schema_components(definition, context)
    all_applicable_definitions = ancestor_definitions + sub_structure_definitions

    for target_schema_definition in all_applicable_definitions:
        sub_definition_validations = target_schema_definition.get_validations()

        for validation in sub_definition_validations:
            validation_name = validation.get("name")
            validator_plugin = list(filter(lambda plugin: plugin.name == validation_name, applicable_validator_plugins))

            if validator_plugin:
                validator_results.append(_apply_validator(definition, target_schema_definition, context, validator_plugin[0]))

    return validator_results


def _apply_validator(
    definition: Definition, target_schema_definition: Definition, context: LanguageContext, validator_plugin: ValidatorPlugin
) -> ValidatorResult:
    """Executes the validator callback on the applicable dictionary structure or substructure."""
    validation_args = []
    defined_validations = target_schema_definition.get_validations()

    for validation in defined_validations:
        if validation.get("name") == validator_plugin.name:
            validation_args = validation.get("arguments") or []

    return validator_plugin.validation_function(definition, target_schema_definition, context, *validation_args)
