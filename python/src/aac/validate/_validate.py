from contextlib import contextmanager
from typing import Generator, Optional

from aac.lang.language_context import LanguageContext
from aac.lang.language_error import LanguageError
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.schema import get_definition_schema_components, get_definition_schema
from aac.lang.definitions.type import remove_list_type_indicator, is_array_type
from aac.lang.hierarchy import get_definition_ancestry
from aac.io.parser import parse
from aac.plugins.plugin_manager import get_validator_plugins, get_enum_validator_plugins
from aac.plugins.validators import ValidatorPlugin, ValidatorFindings, ValidatorResult
from aac.plugins.validators._validator_finding import ValidatorFinding
from aac.validate._validation_error import ValidationError
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
        combined_findings.add_findings([finding for finding_list in definition_findings for finding in finding_list])

    context_definitions_to_validate = active_context.definitions
    definitions_to_validate = definitions + context_definitions_to_validate if validate_context else []
    [validate_each_definition(definition) for definition in definitions_to_validate]

    # This step is necessary to return validated definitions that have had their inheritance applied.
    validated_definitions = [active_context.get_definition_by_name(definition.name) for definition in definitions]
    return ValidatorResult(validated_definitions, combined_findings)


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

    validator_results.append(_validate_primitive_types(definition, context))
    return validator_results


def _apply_validator(
    definition: Definition, target_schema_definition: Definition, context: LanguageContext, validator_plugin: ValidatorPlugin
) -> ValidatorResult:
    """Executes the validator callback on the applicable dictionary structure or substructure."""
    validation_args: list[str] = []
    defined_validations = target_schema_definition.get_validations() or []

    for validation in defined_validations:
        if validation.get("name") == validator_plugin.name:
            validation_args = validation.get("arguments") or []

    return validator_plugin.validation_function(definition, target_schema_definition, context, *validation_args)


def _validate_primitive_types(definition: Definition, context: LanguageContext) -> ValidatorResult:
    """Validates the instances of AaC primitive types."""
    findings = ValidatorFindings()
    findings.add_findings(_recursive_validate_field(definition, get_definition_schema(definition, context), definition.get_top_level_fields(), context))

    return ValidatorResult([definition], findings)


def _recursive_validate_field(source_def: Definition, field_schema: Definition, field_dict: dict, context: LanguageContext) -> list[ValidatorFinding]:
    primitive_types = context.get_primitive_types()
    type_validator_lists = [plugin.get_primitive_validations() for plugin in context.get_plugins() if plugin.get_primitive_validations()]
    enum_validators = [validation for validation_list in type_validator_lists for validation in validation_list]
    validators_dict = {validator.primitive_type: validator for validator in enum_validators}

    findings = []
    schema_fields = field_schema.get_top_level_fields().get("fields", [])
    for field in schema_fields:
        field_name = field.get("name", "")
        field_type = field.get("type", "")
        sanitized_field_type = remove_list_type_indicator(field_type)
        field_values = field_dict.get(field_name) if len(schema_fields) > 1 else field_dict

        if field_values:
            if not is_array_type(field_type):
                field_values = [field_values]

            for field_value in field_values:
                if field_type in primitive_types:
                    validator = validators_dict.get(field_type)

                    if validator:
                        finding = validator.validation_function(source_def, field_value)
                        if finding:
                            findings.append(finding)

                elif context.is_definition_type(sanitized_field_type):
                    new_field_schema = context.get_definition_by_name(sanitized_field_type)
                    findings.extend(_recursive_validate_field(source_def, new_field_schema, field_value, context))

    return findings
