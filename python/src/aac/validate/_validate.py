import logging
from contextlib import contextmanager
from typing import Generator, Any, Optional

from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_ARGUMENTS,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_TYPE,
)
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema_components, get_definition_schema
from aac.lang.definitions.type import remove_list_type_indicator, is_array_type
from aac.lang.hierarchy import get_definition_ancestry
from aac.lang.language_context import LanguageContext
from aac.lang.language_error import LanguageError
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution
from aac.plugins.validators import ValidatorFindings, ValidatorResult
from aac.plugins.validators._validator_finding import ValidatorFinding, FindingSeverity, FindingLocation
from aac.validate._collect_validators import get_applicable_validators_for_definition
from aac.validate._validation_error import ValidationError


@contextmanager
def validated_definition(definition: Definition) -> Generator[ValidatorResult, None, None]:
    """
    Validate a single definition. Does not validate any other definitions in the context.

    Args:
        definition (Definition): The definition to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation([definition], get_active_context(), False)


@contextmanager
def validated_definitions(definitions: list[Definition]) -> Generator[ValidatorResult, None, None]:
    """
    Validate definitions along with all other definitions in the ActiveContext.

    Args:
        definitions (list[Definition]): A list of definitions to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation(definitions, get_active_context())


@contextmanager
def validated_source(source: str) -> Generator[ValidatorResult, None, None]:
    """
    Run validation on a string-based YAML definition or a YAML file.

    Args:
        source (str): The source of the YAML representation of the model.

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    yield _with_validation(parse(source), get_active_context())


def _with_validation(
    user_definitions: list[Definition], language_context: LanguageContext, validate_context: bool = True
) -> ValidatorResult:
    try:
        result = _validate_definitions(user_definitions, language_context, validate_context)

        if result.is_valid():
            return result
        else:
            raise ValidationError(result.get_messages_as_string())
    except LanguageError as error:
        raise ValidationError("Failed to validate content due to an internal language error:\n", *error.args)


def _validate_definitions(
    definitions: list[Definition], language_context: LanguageContext, validate_context: bool
) -> ValidatorResult:
    validation_context = language_context.copy()

    for definition in definitions:
        existing_definition = validation_context.get_definition_by_uid(definition.uid)

        if existing_definition:
            validation_context.update_definition_in_context(definition)
        else:
            validation_context.add_definition_to_context(definition)

    validator_plugins = validation_context.get_definition_validations()

    combined_findings = ValidatorFindings()

    def validate_each_definition(definition: Definition):
        results = _validate_definition(definition, validator_plugins, validation_context)
        definition_findings = [result.findings.get_all_findings() for result in results]
        combined_findings.add_findings([finding for finding_list in definition_findings for finding in finding_list])

    context_definitions_to_validate = validation_context.definitions
    definitions_to_validate = set(definitions + (context_definitions_to_validate if validate_context else []))
    [validate_each_definition(definition) for definition in definitions_to_validate]

    # This step is necessary to return validated definitions that have had their inheritance applied.
    validated_definitions = [validation_context.get_definition_by_name(definition.name) for definition in definitions]
    return ValidatorResult(validated_definitions, combined_findings)


def _validate_definition(
    definition: Definition, validator_plugins: list[DefinitionValidationContribution], language_context: LanguageContext
) -> list[ValidatorResult]:
    """Traverse the definition and validate it according to the validator plugins."""

    validator_results = []

    applicable_validator_plugins = get_applicable_validators_for_definition(definition, validator_plugins, language_context)
    ancestor_definitions = get_definition_ancestry(definition, language_context)
    sub_structure_definitions = get_definition_schema_components(definition, language_context)
    all_applicable_definitions = ancestor_definitions + sub_structure_definitions

    for target_schema_definition in all_applicable_definitions:
        sub_definition_validations = target_schema_definition.get_validations()

        if sub_definition_validations:
            for validation in sub_definition_validations:
                validation_name = validation.get(DEFINITION_FIELD_NAME)
                validator_plugin = list(filter(lambda plugin: plugin.name == validation_name, applicable_validator_plugins))

                if validator_plugin:
                    validator_results.append(
                        _apply_validator(definition, target_schema_definition, language_context, validator_plugin[0])
                    )

    validator_results.append(_validate_primitive_types(definition, language_context))
    return validator_results


def _apply_validator(
    definition: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    validator_plugin: DefinitionValidationContribution,
) -> ValidatorResult:
    """Executes the validator callback on the applicable dictionary structure or substructure."""
    validation_args: list[str] = []
    defined_validations = target_schema_definition.get_validations() or []

    for validation in defined_validations:
        if validation.get(DEFINITION_FIELD_NAME) == validator_plugin.name:
            validation_args = validation.get(DEFINITION_FIELD_ARGUMENTS) or []

    validator_result = None
    try:
        validator_result = validator_plugin.validation_function(definition, target_schema_definition, language_context, *validation_args)
    except Exception as exception:
        exception_message = f"Validator '{validator_plugin.name}' failed with an exception: {exception}"
        finding_location = FindingLocation(validator_plugin.name, definition.source, 0, 0, 0, 0)
        exception_finding = ValidatorFinding(definition, FindingSeverity.ERROR, exception_message, finding_location)
        validator_result = ValidatorResult([definition], ValidatorFindings(findings=[exception_finding]))

    return validator_result


def _validate_primitive_types(definition: Definition, language_context: LanguageContext) -> ValidatorResult:
    """Validates the instances of AaC primitive types."""
    findings = ValidatorFindings()
    definition_schema = get_definition_schema(definition, language_context)
    if definition_schema:
        findings.add_findings(
            _validate_fields(definition, definition_schema, definition.get_top_level_fields(), language_context)
        )

    return ValidatorResult([definition], findings)


def _validate_fields(
    source_def: Definition, field_schema: Definition, field_dict: dict, language_context: LanguageContext
) -> list[ValidatorFinding]:
    findings = []

    primitive_types = language_context.get_primitive_types()

    schema_fields = field_schema.get_top_level_fields().get(DEFINITION_FIELD_FIELDS, [])
    for field in schema_fields:
        field_name = field.get(DEFINITION_FIELD_NAME, "")
        field_type = field.get(DEFINITION_FIELD_TYPE, "")
        sanitized_field_type = remove_list_type_indicator(field_type)
        field_values = field_dict.get(field_name) if len(schema_fields) > 1 else field_dict

        if field_values:
            field_values = field_values if is_array_type(field_type) else [field_values]
            for field_value in field_values:
                if field_type in primitive_types:
                    field_finding = _validate_primitive_field(source_def, field_type, field_value, language_context)
                    if field_finding:
                        findings.append(field_finding)

                elif language_context.is_definition_type(sanitized_field_type):
                    findings.extend(_validate_schema_field(source_def, sanitized_field_type, field_value, language_context))

    return findings


def _validate_primitive_field(
    source_def: Definition, field_type: str, field_value: Any, language_context: LanguageContext
) -> Optional[ValidatorFinding]:
    validators = [
        validator for validator in language_context.get_primitive_validations() if validator.primitive_type == field_type
    ]

    validator_finding = None

    if validators:
        validator, *_ = validators
        try:
            validator_finding = validator.validation_function(source_def, field_value)
        except Exception as exception:
            exception_message = f"Validator '{validator.name}' failed with an exception: {exception}"
            finding_location = FindingLocation(validator.name, source_def.source, 0, 0, 0, 0)
            validator_finding = ValidatorFinding(source_def, FindingSeverity.ERROR, exception_message, finding_location)
    else:
        logging.info(f"No primitive type validation for '{field_type}'")

    return validator_finding


def _validate_schema_field(
    source_def: Definition, field_type: str, field_value: Any, language_context: LanguageContext
) -> list[ValidatorFinding]:
    new_field_schema = language_context.get_definition_by_name(field_type)
    findings = []
    if new_field_schema:
        findings = _validate_fields(source_def, new_field_schema, field_value, language_context)

    return findings
