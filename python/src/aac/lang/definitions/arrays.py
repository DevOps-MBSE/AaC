"""Functions for managing and interacting with definition arrays."""


def remove_list_type_indicator(list_type: str) -> str:
    """Return the AaC type without any trailing list indicator characters '[]'."""
    return list_type.split("[]")[0]


def is_array_type(type: str) -> bool:
    """Returns a boolean indicating if the field is an array of multiple entries."""
    return type.endswith("[]")
