"""Arch-as-Code helper utilities to simplify development.

The aac.util module provides some functionality discovered to be valuable
during the development of aac.  By placing this behavior in a utility
module we prevent code duplication and simplify maintenance.

Avoid adding to this module, always look for ways move these functions into modules with similar functionality.
"""

import os
import logging
from contextlib import contextmanager
from os import chdir, getcwd
from typing import Any


def search(model: dict[str, Any], search_keys: list[str]) -> list:
    """
    Search an AaC model structure by key(s).

    Searches a dict for the contents given a set of keys. Search returns a list of
    the entries in the model that correspond to those keys.  This search will
    traverse the full dict tree, including embedded lists.

        Typical usage example:
        Let's say you have a dict structure parsed from the following AaC yaml.

            data:
            name: MyData
            fields:
                - name: one
                type: string
                - name: two
                type: string
            required:
                - one

        You know the structure of the specification and need to iterate through each field.
        The search utility method simplifies that for you.

            for field in util.search(my_model, ["data", "fields"]):
                print(f"field_name: {field["name"]} field_type {field["type"]}")

        The above example demonstrates a complex type being returned as a dict.  Search will also
        provide direct access to simple types in the model.

            for field_name in util.search(my_model, ["data", "fields", "name"]):
                print(f"field_name: {field_name}")

    Args:
        model: The model to search.  This is often the value taken from the dict returned
            by aac.parser.parse(<aac_file>).
        search_keys: A list of strings representing keys in the model dict hierarchy.

    Returns:
        Returns a list of found data items based on the search keys.

    """
    done = False
    ret_val = []

    keys = search_keys.copy()
    # first make sure there is a key to search for
    if len(keys) == 0 or not isinstance(model, dict):
        logging.error(f"invalid arguments: {keys}, {type(model)}")
        return []

    search_key = keys.pop(0)
    final_key = len(keys) == 0
    model_value = None

    # see if the key exists in the dict
    if search_key in model:
        model_value = model[search_key]

        if final_key:
            if isinstance(model_value, list):
                ret_val = model_value
                done = True
            else:
                ret_val.append(model_value)
                done = True

    # it isn't the final key and the value is a dict, so continue searching
    if not done and isinstance(model_value, dict):
        if isinstance(model_value, dict):
            ret_val = search(model[search_key], keys)
            done = True

    # it isn't the final key and the value is a list, so search each value
    if not done and isinstance(model_value, list):
        for model_item in model_value:

            if isinstance(model_item, dict):
                ret_val = ret_val + (search(model_item, keys))
            else:
                logging.error("keys exceeds depth of the dict to search")
                done = True
        done = True

    # not an error, just zero results
    else:
        logging.info(f"keys[{search_keys}] not found in model")
        done = True

    return ret_val


def get_models_by_type(models: dict[str, dict], root_name: str) -> dict[str, dict]:
    """Gets subset of models of a specific root name.

    The aac.parser.parse() returns a dict of all parsed types.  Sometimes it is
    useful to only work with certain roots (i.e. model or data).  This utility
    method allows a setup of parsed models to be "filtered" to a specific root name.

    Args:
        models: The dict of models to search.
        root_name: The root name to filter on.

    Returns:
        A dict mapping type names to AaC model definitions.
    """
    ret_val = {}
    for key, value in models.items():
        if root_name in value.keys():
            ret_val[key] = value

    return ret_val


@contextmanager
def new_working_dir(directory):
    """Change directories to execute some code, then change back.

    Args:
        directory: The new working directory to switch to.

    Returns:
        The new working directory.

    Example Usage:
        from os import getcwd
        from tempfile import TemporaryDirectory

        print(getcwd())
        with TemporaryDirectory() as tmpdir, new_working_dir(tmpdir):
            print(getcwd())
        print(getcwd())
    """
    current_dir = getcwd()
    try:
        chdir(directory)
        yield getcwd()
        chdir(current_dir)
    except Exception as e:
        chdir(current_dir)
        raise e


def is_path_name(string: str) -> bool:
    """Return True if string is a pathname; False, otherwise."""
    return os.path.lexists(string)
