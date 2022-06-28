import logging
import re
from typing import Any

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.type import is_array_type
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_reference_fields(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
    """
    Validates that the content of all specified reference fields is properly formatted.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []
    reference_field_names = validation_args
    schema_defined_fields_as_list = target_schema_definition.get_top_level_fields().get("fields") or []
    schema_defined_fields_as_dict = {field.get("name"): field for field in schema_defined_fields_as_list}

    def validate_dict(dict_to_validate: dict) -> None:
        for reference_field_name in reference_field_names:
            field_value = dict_to_validate.get(reference_field_name)
            field_type = schema_defined_fields_as_dict.get(reference_field_name, {}).get("type")

            # field type must be reference
            if field_type != "reference":
                non_reference_field = f"Reference format validation cannot be performed on non-reference field '{reference_field_name}'.  Type is '{field_type}'"
                error_messages.append(non_reference_field)
                logging.debug(non_reference_field)

            # field must not be empty
            elif field_value is None:
                missing_reference_field = f"Reference field '{reference_field_name}' value is missing"
                error_messages.append(missing_reference_field)
                logging.debug(missing_reference_field)

            # field must be contain a parsable reference value
            elif not _is_reference_parsable(reference_field_name, field_value):
                invalid_reference_format = f"Reference field '{reference_field_name}' is not properly formatted: {field_value}"
                error_messages.append(invalid_reference_format)
                logging.debug(invalid_reference_format)


    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)


def _is_reference_parsable(field_name: Any, field_value: Any) -> bool:
    """
    Return a boolean indicating if the reference can be successfully parsed.
    Reference fields contain a sequence of reference terms separated by a period.
    Each reference term contains an identifier and an optional selector.  The identifier
    is just a string correlating to a name in a schema structure.  Schema hierarchy is
    traversed using dot notation (e.g. parent.child.grandchild).  The optional selector
    is provided within parameters and contains a child field name and value (e.g. parent(name="MyModel")).
    A reference is parsable if the reference convention is followed regardless of
    whether the reference results in identification of a valid reference target.
    """
    # This assumes input is not None

    found_invalid_segment = False

    for segment in field_value.split('.'):

        if not re.search(".*(\(\w+\=(\"\w+(\s\w+)*\"|\w+)\))?", segment):  # this regex needs work
            # segment content consistent with segment formatting
            found_invalid_segment = True

    return not found_invalid_segment
