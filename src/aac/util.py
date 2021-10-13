"""Arch-as-Code helper utilities to simplify development.

The aac.util module provides some functionallity discovered to be valuable
during the development of aac.  By placing this behavior in a utility
module we prevent code duplication and simplify maintenance.
"""
import os
import logging
from typing import Any
import yaml
from aac import parser

PRIMITIVES: list[str] = []
ROOT_NAMES: list[str] = []
AAC_MODEL: dict[str, dict] = {}


def search(model: dict[str, Any], search_keys: list[str]) -> list:
    """Search an AaC model structure by key(s).

    Searches a dict for the contents given a set of keys. Search returns a list of
    the entries in the model that correcpond to those keys.  This search will
    traverse the full dict tree, including embeded lists.

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

            for field_name in util.serach(my_model, ["data", "fields", "name"]):
                print(f"field_name: {field_name}")

    Args:
        model: The model to search.  This is often the value taken from the dict returned
            by aac.parser.parse(<aac_file>).
        search_keys: A list of strings representing keys in the model dict heirarchy.

    Returns:
        Returns a list of found data items based on the search keys.

    """

    done = False
    ret_val = []

    keys = search_keys.copy()
    # first make sure there is a key to search for
    if len(keys) == 0 or not isinstance(model, dict):
        logging.error(f"invalid arguments: [{keys}], {type(model)}")
        return []

    search_key = keys.pop(0)
    final_key = len(keys) == 0
    model_value = model[search_key]

    # see if the key exists in the dict
    if search_key in model:
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
            # print(model_item)
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


def get_aac_spec() -> tuple[dict[str, dict], dict[str, dict]]:
    """
    Gets the specification for Architecture-as-Code iteself.  The AaC model specification is
    defined as an AaC model and is needed for model validation.

    Returns:
        Returns a tuple (aac_data, aac_enums), where aac_data is a dict of the AaC model spec
        with root types of data and aac_enums is a dict of the AaC model spec with root types
        of enum.

    """

    global AAC_MODEL
    if len(AAC_MODEL.keys()) > 0:
        # already parsed, just return cached values
        aac_data = get_models_by_type(AAC_MODEL, "data")
        aac_enums = get_models_by_type(AAC_MODEL, "enum")
        return aac_data, aac_enums

    # get the AaC.yaml spec for architecture modeling
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    relpath_to_aac_yaml = "../../model/aac/AaC.yaml"
    aac_model_file = os.path.join(this_file_path, relpath_to_aac_yaml)

    AAC_MODEL = parser.parseFile(aac_model_file, False)
    aac_data = get_models_by_type(AAC_MODEL, "data")
    aac_enums = get_models_by_type(AAC_MODEL, "enum")

    return aac_data, aac_enums


def get_aac_spec_as_yaml() -> str:
    """Get the base AaC spec in YAML.

    Utility to provide the current base AaC model specification (including plugin extensions)
    in an easy to read yaml format (just as it is defined internally).

    Returns:
        Returns a string containing YAML for the current AaC spec.  Each model entry is separated
        by the "---" yaml syntax representing separate files to be parsed.
    """
    aac_data, aac_enums = get_aac_spec()
    aac_model = aac_data | aac_enums
    aac_yaml = ""
    is_first = True
    for aac_name in aac_model.keys():
        # put in the separator for all but the first
        if is_first:
            is_first = False
        else:
            aac_yaml = aac_yaml + "---\n"

        aac_yaml = aac_yaml + yaml.dump(aac_model[aac_name]) + "\n"
    return aac_yaml


def extend_aac_spec(parsed_model: dict[str, dict]):
    """Applies an extension to the base AaC model specification.

    The AaC base model specification is used for validation. This method allows
    you to apply an extention (modeled as an ext root type) to modify that
    base model specification.

    Args:
        parsed_model: The result of aac.parser.parse(<aac_file>).
    """
    global AAC_MODEL

    apply_me = parsed_model.copy()
    exts = get_models_by_type(apply_me, "ext")
    for ext_type in exts:
        del apply_me[ext_type]
    AAC_MODEL = AAC_MODEL | apply_me


def get_primitives(reload: bool=False) -> list[str]:
    """Gets the list of primitives as defined in the AaC model specifictaion.

    Args:
        reload: If True the cached primitive values will be reloaded.
            Default is False.

    Returns:
        A list of strings, one entry for each primitive type in the AaC model specification.
    """

    global PRIMITIVES

    if len(PRIMITIVES) == 0 or reload:
        _, aac_enums = get_aac_spec()
        PRIMITIVES = search(aac_enums["Primitives"], ["enum", "values"])

    return PRIMITIVES


def get_roots(reload: bool=False) -> list[str]:
    """Gets the list of root names as defined in the AaC model specifictaion.

    Args:
        reload: If True the cached root name values will be reloaded.
            Default is False.

    Returns:
        A list of strings, one entry for each root name in the AaC model specification.
    """

    global ROOT_NAMES

    if len(ROOT_NAMES) == 0 or reload:
        aac_data, _ = get_aac_spec()
        ROOT_NAMES = search(aac_data["root"], ["data", "fields", "name"])

    return ROOT_NAMES


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
