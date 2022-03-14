"""Contains functionality to support validating AaC architecture files."""
from attr import attrib, attrs, validators, Factory
from contextlib import contextmanager
import itertools

from aac import plugins


class ValidationError(RuntimeError):
    """An error that represents a model with invalid components and/or structure."""

    pass


@attrs(slots=True, auto_attribs=True)
class ValidationResult:
    """Represents the result of validating a model.

    Attributes:
        messages (list[str]): A list of messages to be provided as feedback for the user.
        model (dict): The model that was validated; if the model is invalid, None.
    """

    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))
    model: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))


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


def _preview_validate(model: dict) -> None:
    """Return all validation errors for the model.

    This function validates the target model against the core AaC Spec and any actively installed
    plugin data, enum, and extension definitions.

    Args:
        model: The model to validate.

    Raises:
        Raises a ValidationError if any errors are found when validating the model.
    """
    plugin_manager = plugins.get_plugin_manager()
    registered_validators = plugin_manager.hook.register_validators()

    print(list(itertools.chain(*registered_validators)))
