from contextlib import contextmanager
from copy import deepcopy

from aac import plugins
from aac.lang import ActiveContext
from aac.lang.context_manager import get_active_context
from aac.parser import ParsedDefinition
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.validate import ValidationError, ValidationResult, get_applicable_validators_for_definition


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

    active_context = get_active_context()
    registered_validators = plugins.get_validator_plugins()

    validation_results = [
        _validate_definition(user_definition, registered_validators, active_context) for user_definition in user_definitions
    ]
    invalid_results = list(filter(filter_out_valid_result, validation_results))

    if len(invalid_results) > 0:
        raise ValidationError(f"Invalid definitions:\n {invalid_results}")
    else:
        yield validation_results


def _validate_definition(
    definition: ParsedDefinition, registered_validators: list[ValidatorPlugin], context: ActiveContext
) -> list[ValidatorResult]:
    """
    Validate the definition and return all validation errors.

    This function validates the target model against the core AaC Spec and any actively installed
    plugin data, enum, and extension definitions.

    Args:
        definition: The definition to validate.

    Raises:
        Raises a ValidationError if any errors are found when validating the model.
    """

    def apply_validator_plugin(applicable_validator: ValidatorPlugin) -> ValidatorResult:
        applicable_validator.validation_function(definition)

    applicable_validators = get_applicable_validators_for_definition(definition, registered_validators, context)
    result = ValidationResult(definition=deepcopy(definition))

    validation_results = list(map(apply_validator_plugin, applicable_validators))

    # TODO perform an actual check here.
    if len(validation_results) > 0:
        result.is_valid = True

    return result
