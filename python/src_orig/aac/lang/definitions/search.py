"""Various functions that provide the ability to search through a definition's structure."""

import logging
from typing import Any

from aac.lang.definitions.definition import Definition


def search(model: dict[str, Any], search_keys: list[str]) -> list:
    """
    Search an AaC model structure by key(s).

    Searches a dict for the contents given a set of keys. Search returns a list of
    the entries in the model that correspond to those keys.  This search will
    traverse the full dict tree, including embedded lists.

        Typical usage example:
        Let's say you have a dict structure parsed from the following AaC yaml.

            schema:
              name: MyData
              fields:
                  - name: one
                    type: string
                  - name: two
                    type: string
              validation:
                - name: Required fields are present
                  arguments:
                    - one

        You know the structure of the specification and need to iterate through each field.
        The search utility method simplifies that for you.

            for field in definition_helpers.search(my_model, ["schema", "fields"]):
                print(f"field_name: {field["name"]} field_type {field["type"]}")

        The above example demonstrates a complex type being returned as a dict.  Search will also
        provide direct access to simple types in the model.

            for field_name in definition_helpers.search(my_model, ["schema", "fields", "name"]):
                print(f"field_name: {field_name}")

    Args:
        model: The model to search.  This is often the value taken from the dict returned
            by aac.io.parser.parse(<aac_file>).
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


def search_definition(definition: Definition, search_keys: list[str]) -> list:
    """
    Search an AaC definition structure by key(s).

    Searches a Definition for a subset of the definition contents given a set of keys.
    Search returns a list of  entries in the definition that correspond to those keys. This search
    will traverse the entire definition's structure.

        Typical usage example:
        Let's say you have a definition structure parsed from the following AaC yaml.

            schema:
              name: MyData
              fields:
                - name: one
                  type: string
                - name: two
                  type: string
              validation:
                - name: Required fields are present
                  arguments:
                  - one

        You know the structure of the specification and need to iterate through each field.
        The search utility method simplifies that for you.

            for field in definition_helpers.search(my_model, ["schema", "fields"]):
                print(f"field_name: {field["name"]} field_type {field["type"]}")

        The above example demonstrates a complex type being returned as a dict.  Search will also
        provide direct access to simple types in the model.

            for field_name in definition_helpers.search(my_definition, ["schema", "fields", "name"]):
                print(f"field_name: {field_name}")

    Args:
        definition: The definition to search.
        search_keys: A list of strings representing keys in the model dict hierarchy.

    Returns:
        Returns a list of found data items based on the search keys.
    """
    return search(definition.structure, search_keys)
