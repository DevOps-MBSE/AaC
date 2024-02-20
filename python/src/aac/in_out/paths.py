"""Module for shared path functions."""

import logging
import os
import unicodedata
from urllib.parse import unquote


def sanitize_filesystem_path(file_path: str) -> str:
    r"""
    Sanitizes user-provided file path strings to prevent injection and tampering of filesystem paths.

    This function does not determine if a user can write to the path location, it only sanitizes and evaluates the
    path to a full path. The user must still check that the path is a valid destination.

    This function performs the following sanitizing actions:

        * Removes any URL encoding
        * Converts the path to an ASCII encoding
        * Replaces instances of / or \ with os-specific path separators
        * Normalizes the path
        * Determines the realpath if symbolic links are used
        * Ensures that the path is an absolute path

    Path Traversal Security References:

        * OWASP https://owasp.org/www-community/attacks/Path_Traversal

    Args:
        file_path (str): The file path to sanitize

    Returns:
        A sanitized filepath.
    """

    # Loop and unquote until there are no more n-levels of url encoding.
    decoded_url_path = file_path
    while "%" in decoded_url_path:
        unquoted_path = unquote(decoded_url_path)
        if unquoted_path == decoded_url_path:
            break
        else:
            decoded_url_path = unquoted_path

    null_byte_stripped_path = decoded_url_path.replace("\0", "")
    ascii_string_file_path = unicodedata.normalize("NFKD", null_byte_stripped_path).encode("ascii", "replace").decode()

    # Replace instances of \ / with os-specific filepath separator
    os_specific_separator_file_path = ascii_string_file_path.replace("/", os.path.sep)
    os_specific_separator_file_path = os_specific_separator_file_path.replace("\\", os.path.sep)

    normalized_path = os.path.normpath(os_specific_separator_file_path)
    real_path = os.path.realpath(normalized_path)
    abs_norm_path = os.path.abspath(real_path)
    logging.info(f"Sanitized and converted path '{file_path}' to '{abs_norm_path}'.")

    return abs_norm_path


def is_same_file(path1: str, path2: str) -> bool:
    """
    Return whether or not path1 and path2 refer to the same file.

    Args:
        path1 (str): The first path to compare.
        path2 (str): The second path to compare.

    Returns:
        Return True if both paths refer to the same file; False, otherwise.
    """
    return os.path.normcase(path1) == os.path.normcase(path2)
