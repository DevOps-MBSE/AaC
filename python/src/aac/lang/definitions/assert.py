"""Provide definition-specific assertions and debug logging."""

def does_field_match_defined_type(field_content: dict, field_type: str) -> bool:
    """
    Return a boolean indicating if the field content matches its defined type.

    For instance, if a field is defined as an array type, then this function
    returns True if the field content is an array or False if the content is
    not an array.

    Args:
        field_content (dict): A dict representing the field content to assert on

    """
