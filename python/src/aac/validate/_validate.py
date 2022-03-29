from contextlib import contextmanager
from iteration_utilities import flatten

from aac.lang.context_manager import get_active_context
from aac.parser import ParsedDefinition
from aac.plugins.plugin_manager import get_validator_plugins
from aac.plugins.validators import ValidatorResult
from aac.validate import ValidationResult
from aac.validate._validate_definition import validate_definition


@contextmanager
def validate_definitions(user_definitions: list[ParsedDefinition]) -> ValidationResult:
    """Validate user-defined definitions along with the definitions in the ActiveContext.

    Args:
        user_definitions (list[ParsedDefinition]): A list of user-defined definitions to validate

    Yields:
        A ValidationResults:py:class:`aac.validate.ValidationResult` indicating the result.
    """
    registered_validators = get_validator_plugins()
    active_context = get_active_context()

    def validate_each_definition(definition: ParsedDefinition) -> list[ValidatorResult]:
        return validate_definition(definition, registered_validators, active_context)

    validator_results = list(flatten(map(validate_each_definition, user_definitions)))
    validator_messages = []
    invalid_results = []

    for result in validator_results:
        validator_messages.extend(result.messages)
        if not result.is_valid:
            invalid_results.extend(result.messages)

    yield ValidationResult(validator_messages, len(invalid_results) < 1)
