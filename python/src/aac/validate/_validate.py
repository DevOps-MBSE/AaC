from contextlib import contextmanager
from copy import deepcopy

from aac import plugins
from aac.parser import ParsedDefinition
from aac.validate._validation_result import ValidationResult
from aac.validate._validation_error import ValidationError
from aac.validate._validator_plugin import ValidatorPlugin


@contextmanager
def validate_definitions(user_definitions: list[ParsedDefinition]) -> list[ValidationResult]:
    """Validate user-defined definitions along with the definitions in the ActiveContext.

    Args:
        user_definitions (list[ParsedDefinition]): A list of user-defined definitions to validate

    Returns:
        A list of ValidationResults :py:class:`aac.validate.ValidationResult` for each validated definition.

    Raises:
        ValidationError: Raised when any of the definitions are invalid.
    """

    def filter_out_valid_result(validation_result: ValidationResult):
        return not validation_result.is_valid

    plugin_manager = plugins.get_plugin_manager()
    registered_validators = plugin_manager.hook.register_validators()

    validation_results = [_validate_definition(user_definition, registered_validators) for user_definition in user_definitions]
    invalid_results = list(filter(filter_out_valid_result, validation_results))

    if len(invalid_results) > 0:
        raise ValidationError(f"Invalid definitions:\n {invalid_results}")
    else:
        yield validation_results


def _validate_definition(definition: ParsedDefinition, registered_validators: list[ValidatorPlugin]) -> ValidationResult:
    """
    Validate the definition and return all validation errors.

    This function validates the target model against the core AaC Spec and any actively installed
    plugin data, enum, and extension definitions.

    Args:
        definition: The definition to validate.

    Raises:
        Raises a ValidationError if any errors are found when validating the model.
    """
    def apply_validator_plugin(applicable_validator: ValidatorPlugin):
        applicable_validator.validation_function(definition)

    print(registered_validators)
    print(definition)

    applicable_validators = _collect_applicable_validations(definition, registered_validators)
    result = ValidationResult(definition=deepcopy(definition))

    validation_results = list(map(apply_validator_plugin, applicable_validators))

    # TODO perform an actual check here.
    if len(validation_results) > 0:
        result.is_valid = True

    return result


def _collect_applicable_validations(definition: ParsedDefinition, registered_validators: list[ValidatorPlugin]) -> list[ValidatorPlugin]:

    # TODO: Use the definition root to look up the definition by name (i.e. "data", "enum", "etc")
    definition_root = definition.get_root_key()

    # Based on the root type, retreive some applicable validators.
    return registered_validators
