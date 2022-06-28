import logging
import re
from typing import Any

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search
from aac.lang.definitions.type import is_array_type
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_reference_targets(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
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

            # field must reference an existing target
            elif not _reference_target_exists(reference_field_name, field_value, language_context):
                invalid_reference_target = f"Reference field '{reference_field_name}' does not have a defined target: {field_value}"
                error_messages.append(invalid_reference_target)
                logging.debug(invalid_reference_target)


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

def _reference_target_exists(field_name: Any, field_value: Any, language_context: LanguageContext) -> bool:
    """
    Return a boolean indicating if the reference target exists in the defined model.
    """
    # This assumes input is not None and is valid

    # First get the root element and optional selector
    segments = field_value.split('.')

    # get the root so we can pull the right definitions from the language context
    root, _, _, _ = _get_segment_content(segments[0])

    # recursively filter through the definitions by filtering out definitions using selectors
    keepers = _process_segment([], segments, language_context.get_definitions_by_root_key(root), language_context)

    return len(keepers) > 0


def _process_segment(prefix: list[str], segments: list[str], definitions: list[Definition], language_context: LanguageContext) -> list[Definition]:
    """
    This should process segments recursively
    """
    if len(segments) == 0:
        # everything has been processed, so return what was found in the previous recursion
        return definitions

    keepers = []
    key, selector, selector_field, selector_value = _get_segment_content(segments[0])

    if key in language_context.get_root_keys():
        # handle the root key
        if selector:
            # handle root level selector
            for definition in definitions:
                if definition.get_top_level_fields()[selector_field] == selector_value:
                    keepers.append(definition)
        else:
            # no root level selector, so just keep all definitions and move on
            keepers.extend(definitions)
    else:
        # handle non-root keys
        prefix.pop()  # ignore root prefix
        for definition in definitions:
            def_dict = definition.get_top_level_fields()
            key_list = []
            for val in prefix:
                key_list.append(val)
                def_dict = def_dict[val]
            # we now have worked through the prefix keys to the dict for evaluation
            if key in def_dict.keys():
                if selector:
                    # since there is a selector, only keep the definition if it contains the specified selector field and value
                    # note that selectors filter based on child field values
                    value_for_key = def_dict[key]
                    if type(value_for_key) is list:
                        for item in value_for_key:
                            if str(item[selector_field]) == str(selector_value):  # casting these seems like a hack

                                keepers.append(definition)
                                break
                    else:
                        if str(value_for_key[selector_field]) == str(selector_value):  # casting these seems like a hack
                            keepers.append(definition)
                else:
                    # if there's no selector, keep the definition since it contains the segment key
                    keepers.append(my_definition)

    if len(keepers) == 0:
        return []

    nxt_prefix = prefix
    nxt_prefix.append(key)
    return _process_segment(nxt_prefix, segments[1:], keepers, language_context)


def _get_segment_content(segment: Any) -> tuple:

    element = ""
    selector = ""
    selector_field = ""
    selector_value = ""
    if segment.find('(') > 0 :
        element = segment.partition('(')[0]
        selector = segment[segment.find('(')+1:segment.find(')')]
        selector_field, selector_value = selector.split("=")
        selector_value = selector_value.strip('\"')  # remove quotes if they exist
    else:
        element = segment

    return (element, selector, selector_field, selector_value)
