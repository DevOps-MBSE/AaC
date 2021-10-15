from aac import util


def is_valid(model: dict) -> bool:
    """Check if MODEL is valid per the AaC DSL.

    :return: Return True if MODEL is valid; False, otherwise.
    """
    return len(get_all_errors(model)) == 0


def get_all_errors(model: dict) -> list:
    """Return all validation errors for MODEL.

    :return: Return a list of all the validation errors found for MODEL. If the MODEL is valid,
    return an empty list.
    """
    errors = []
    enum = model["enum"]

    if "name" not in enum.keys():
        errors.append('missing required field property: "name"')

    if "values" not in enum.keys():
        errors.append('missing required field property: "values"')

    if "name" in enum.keys() and not isinstance(enum["name"], str):
        errors.append('wrong type for field property: "values"')

    if "values" in enum.keys() and not isinstance(enum["values"], list):
        errors.append('wrong type for field property: "name"')

    return errors
