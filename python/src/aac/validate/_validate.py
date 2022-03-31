from contextlib import contextmanager
from iteration_utilities import flatten

from aac.lang.context_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.parser import parse
from aac.plugins.plugin_manager import get_validator_plugins
from aac.plugins.validators import ValidatorResult
from aac.validate import ValidationResult, ValidationError
from aac.validate._validate_definition import validate_definition


@contextmanager
def validate_definitions(user_definitions: list[Definition]) -> ValidationResult:
    """Validate user-defined definitions along with the definitions in the ActiveContext.

    Args:
        user_definitions (list[Definition]): A list of user-defined definitions to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    result = _validate_definitions(user_definitions)
    if result.is_valid:
        yield result
    else:
        raise ValidationError("Failed to validate content with errors:", ".\n".join(result.messages))


@contextmanager
def validate_source(source: str) -> ValidationResult:
    """Run validation on a string-based YAML definition or a YAML file.

    Args:
        source (str): The source of the YAML representation of the model.

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    result = _validate_definitions(parse(source))
    if result.is_valid:
        yield result
    else:
        raise ValidationError("Failed to validate content with errors:", ".\n".join(result.messages))


def _validate_definitions(user_definitions: list[Definition]) -> ValidationResult:
    registered_validators = get_validator_plugins()
    active_context = get_active_context()
    active_context.add_definitions_to_context(user_definitions)

    def validate_each_definition(definition: Definition) -> list[ValidatorResult]:
        return validate_definition(definition, registered_validators, active_context)

    validator_results = list(flatten(map(validate_each_definition, user_definitions)))
    validator_messages = []
    invalid_results = []

    for result in validator_results:
        validator_messages.extend(result.messages)
        if not result.is_valid:
            invalid_results.extend(result.messages)

    return ValidationResult(user_definitions, validator_messages, len(invalid_results) < 1)
