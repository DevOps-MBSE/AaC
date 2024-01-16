"""Module to comb directories and identify AaC files."""
import logging
import os

from aac.in_out.constants import YAML_DOCUMENT_EXTENSION, AAC_DOCUMENT_EXTENSION
from aac.in_out.parser import parse, ParserError
from aac.in_out.files.aac_file import AaCFile


def find_aac_files(root_directory_to_search: str) -> list[AaCFile]:
    """Return a list of paths to AaC files in or under the root directory."""
    aac_files = []

    root_dir_abs_path = os.path.abspath(root_directory_to_search)
    if os.path.isdir(root_dir_abs_path):
        directory_results = os.walk(root_dir_abs_path)
        for directory_path, _, filenames in directory_results:
            for filename in filenames:
                filepath = os.path.join(directory_path, filename)
                if is_aac_file(filepath):
                    aac_files.append(AaCFile(filepath, True, False))
    else:
        logging.error(f"Root path '{root_dir_abs_path}' for AaC file discovery is not a directory.")

    return aac_files


def is_aac_file(filepath: str) -> bool:
    """Test if a target file is considered a valid AaC file."""
    _, file_ext = os.path.splitext(filepath)

    is_valid_aac_file = False
    if file_ext == YAML_DOCUMENT_EXTENSION or file_ext == AAC_DOCUMENT_EXTENSION:
        try:
            parse(filepath)
        except ParserError as error:
            logging.error(f"File '{filepath}' is not a valid AaC file. Reason: {error.errors}")
        except Exception as error:
            logging.error(f"File '{filepath}' could not be parsed. Reason: {error}")
        else:
            is_valid_aac_file = True

    return is_valid_aac_file
