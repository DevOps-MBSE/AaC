"""Contains functionality to support validating AaC architecture files."""
from contextlib import contextmanager

from aac import plugins
from aac.parser import ParsedDefinition
from aac.validate._validator_plugin import ValidatorPlugin
from aac.validate._validation_error import ValidationError
from aac.validate._validation_result import ValidationResult

__all__ = (
    ValidationError.__name__,
    ValidationResult.__name__,
    ValidatorPlugin.__name__,
)


@contextmanager
def preview_validation(model_producer: callable, source: str, **kwargs) -> ValidationResult:
    """Run validation on the model returned by func.

    Args:
        model_producer (callable): A function that returns an Architecture-as-Code model. The
                                       first argument accepted by model_producer must be the source
                                       of the YAML representation of the model.
        source (str): The source of the YAML representation of the model.
        kwargs (dict): Any additional arguments that should be passed on to model_producer.

    Returns:
        If the model returned by model_producer is valid, it is returned. Otherwise, None is returned.
    """
    result = ValidationResult()
    try:
        result.model = model_producer(source, **kwargs)
        _preview_validate(result.model)
        result.messages.append(f"{source} is valid")
        yield result
    except ValidationError as ve:
        raise ValidationError(source, *ve.args)


def _preview_validate(definition: ParsedDefinition) -> None:
    """Return all validation errors for the definition.

    This function validates the target model against the core AaC Spec and any actively installed
    plugin data, enum, and extension definitions.

    Args:
        definition: The definition to validate.

    Raises:
        Raises a ValidationError if any errors are found when validating the model.
    """
    plugin_manager = plugins.get_plugin_manager()
    registered_validators = plugin_manager.hook.register_validators()

    print(registered_validators)
