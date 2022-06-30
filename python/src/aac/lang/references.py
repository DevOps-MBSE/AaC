"""Module for AaC Language functions related to definition references."""

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition


def get_definition_type_references_from_list(
    source_definition: Definition, definitions_to_search: list[Definition]
) -> list[Definition]:
    """
    Return a subset of Definitions that reference the source_definition.

    Args:
        source_definition (Definition): The definition that is being referenced
        definitions_to_search (list[Definition]): The definitions to search through for references

    Return:
        A list of Definitions that reference the source_definition
    """

    def filter_definitions_by_reference(definition_to_filter: Definition) -> bool:
        return f"type: {source_definition.name}" in definition_to_filter.to_yaml()

    return list(filter(filter_definitions_by_reference, definitions_to_search))


def is_reference_format_valid(reference_field_value: str = None) -> tuple[bool, str]:
    """Returns boolean and string tuple indicating if the reference field is properly formatted for processing."""
    # This assumes input is not None
    if reference_field_value is None:
        return False, "Reference must have content"

    found_invalid_segment = False
    message = "Reference OK"

    for segment in reference_field_value.split('.'):

        # Rule: segment must have content
        if len(segment) == 0:
            message = "Failed rule: segment must have content"
            found_invalid_segment = True
            break

        open_peren = segment.find('(')
        close_peren = segment.find(')')
        equals = segment.find('=')

        # Rule: if there is an open peren designating a selector, there must be a corresponding close peren...and vice versa
        if not ((open_peren < 0 and close_peren < 0) or (open_peren > 0 and close_peren > 0)):
            message = "Failed rule: if there is an open peren designating a selector, there must be a corresponding close peren...and vice versa"
            found_invalid_segment = True
            break

        # Rule:  if there is a selector, it must contain an equals with content on either side
        if open_peren >= 0 and (equals < 0 or (open_peren + 1 == equals) or (equals + 1 == close_peren)):
            message = "Failed rule: if there is a selector, it must contain an equals with content on either side"
            found_invalid_segment = True
            break

        # break the segment into it's parts (i.e. key(selector_field=selector_value))
        key, selector, selector_field, selector_value = _get_reference_segment_content(segment)

        # Rule: there must be content before the selector
        if len(key) == 0:
            message = "Failed rule: there must be content before the selector"
            found_invalid_segment = True
            break

        # Rule: names only contain allowed values
        if _has_disallowed_characters(key) or (len(selector_field) > 0 and _has_disallowed_characters(selector_field)):
            message = "Failed rule: names only contain allowed values"
            found_invalid_segment = True
            break

    return not found_invalid_segment, message


def _has_disallowed_characters(test_me: str) -> bool:
    disallowed = set("~`!@#$%^&*()=+\\|[]{}'\";:/?,.<> ")
    return any((c in disallowed) for c in test_me)


def get_reference_target_definitions(reference_field_value: str, language_context: LanguageContext) -> list[Definition]:
    """
    Return a boolean indicating if the reference target exists in the defined model.

    Args:
        reference_field_value (str): The definition that is being referenced
        language_context (LanguageContext): The language context to search.

    Search the language context for target definitions which satisfy the reference.  A matching definition
    must have all fields referenced in the selector and must contain fields which satisfy any selectors defined in
    the reference.

    It is assumed that the reference_field_value is a properly formatted reference primitive field.  If it is not,
    an empty list will be returned.  You can test this using the is_reference_format_valid() method prior to getting
    the reference target definitions if you have any uncertainty.
    """

    # Check that input is not None and is valid
    if not is_reference_format_valid(reference_field_value)[0]:
        return []

    # First get the root element and optional selector
    segments = reference_field_value.split('.')

    # get the root so we can pull the right definitions from the language context
    root, _, _, _ = _get_reference_segment_content(segments[0])

    # recursively filter through the definitions by filtering out definitions using selectors
    keepers = _process_segment([], segments, language_context.get_definitions_by_root_key(root), language_context)

    return keepers


def _process_segment(prefix: list[str], segments: list[str], definitions: list[Definition], language_context: LanguageContext) -> list[Definition]:
    """This should process segments recursively."""
    if len(segments) == 0:
        # everything has been processed, so return what was found in the previous recursion
        return definitions

    keepers = []
    key, selector, selector_field, selector_value = _get_reference_segment_content(segments[0])

    if key in language_context.get_root_keys():
        # handle root key
        keepers.extend(_process_root(selector, selector_field, selector_value, definitions))

    else:
        # handle non-root keys
        keepers.extend(_process_non_root(key, prefix, selector, selector_field, selector_value, definitions))

    if len(keepers) == 0:
        return []

    nxt_prefix = prefix
    nxt_prefix.append(key)
    return _process_segment(nxt_prefix, segments[1:], keepers, language_context)


def _process_root(selector: str, selector_field: str, selector_value: str, definitions: list[Definition]) -> list[Definition]:
    """Return definitions that match the root selector.  If no selector, return all definitions."""
    keepers = []
    if selector:
        # handle root level selector
        for definition in definitions:
            if str(definition.get_top_level_fields()[selector_field]) == str(selector_value):
                keepers.append(definition)
    else:
        # no root level selector, so just keep all definitions and move on
        keepers.extend(definitions)
    return keepers


def _process_non_root(key: str, prefix: list[str], selector: str, selector_field: str, selector_value: str, definitions: list[Definition]) -> list[Definition]:
    # initialize return value as empty string
    keepers = []
    for definition in definitions:
        top_level_fields = definition.get_top_level_fields()
        dict_list = _drill_into_nested_dict(prefix[1:], top_level_fields)

        for def_dict in dict_list:
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
                    keepers.append(definition)
    return keepers


def _drill_into_nested_dict(search_keys: list[str], search_me: dict) -> list:
    if len(search_keys) == 0:
        return [search_me]

    if search_keys[0] in search_me.keys():
        next_level = search_me[search_keys[0]]
        if isinstance(next_level, list):
            items_to_return = []
            # iterate through next level items and continue search
            for item in next_level:
                if isinstance(item, dict):
                    i = _drill_into_nested_dict(search_keys[1:], item)
                    if len(i) > 0:
                        items_to_return.extend(i)
            return items_to_return
        elif isinstance(next_level, dict):
            return _drill_into_nested_dict(search_keys[1:], next_level)
        else:
            return []
    return []


def _get_reference_segment_content(segment: str) -> tuple:

    element = ""
    selector = ""
    selector_field = ""
    selector_value = ""
    if segment.find('(') > 0:
        element = segment.partition('(')[0]
        selector = segment[segment.find('(') + 1:segment.find(')')]
        selector_field, selector_value = selector.split("=")
        selector_value = selector_value.strip('\"')  # remove quotes if they exist
    else:
        element = segment

    return (element, selector, selector_field, selector_value)
