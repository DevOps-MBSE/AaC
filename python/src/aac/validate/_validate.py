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
from aac.plugins.validators._validator_findings import ValidatorFindings
from aac.validate._collect_validators import get_applicable_validators_for_definition


@contextmanager
def validated_definition(definition: Definition) -> Generator[ValidatorResult, None, None]:
    """
    Validate a single definition. Does not validate any other definitions in the context.

    Args:
        definition (Definition): The definition to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation([definition], False)


@contextmanager
def validated_definitions(definitions: list[Definition]) -> Generator[ValidatorResult, None, None]:
    """
    Validate definitions along with all other definitions in the ActiveContext.

    Args:
        definitions (list[Definition]): A list of definitions to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation(definitions)


@contextmanager
def validated_source(source: str) -> Generator[ValidatorResult, None, None]:
    """
    Run validation on a string-based YAML definition or a YAML file.

    Args:
        source (str): The source of the YAML representation of the model.

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation(parse(source))


def _with_validation(user_definitions: list[Definition], validate_context: bool = True) -> ValidatorResult:
    try:
        result = _validate_definitions(user_definitions, validate_context)

        if result.is_valid():
            return result
        else:
            raise ValidationError(result.get_messages_as_string())
    except LanguageError as error:
        raise ValidationError("Failed to validate content due to an internal language error:\n", *error.args)


def _validate_definitions(definitions: list[Definition], validate_context: bool) -> ValidatorResult:
    active_context = get_active_context()
    active_context.add_definitions_to_context(definitions)

    validator_plugins = get_validator_plugins()

    combined_findings = ValidatorFindings()

    def validate_each_definition(definition: Definition):
        results = _validate_definition(definition, validator_plugins, active_context)
        definition_findings = [result.findings.get_all_findings() for result in results]
        combined_findings.add_findings(list(flatten(definition_findings)))

    context_definitions_to_validate = active_context.definitions
    definitions_to_validate = definitions + context_definitions_to_validate if validate_context else []
    [validate_each_definition(definition) for definition in definitions_to_validate]
    return ValidatorResult(definitions, combined_findings)


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

        if sub_definition_validations:
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
