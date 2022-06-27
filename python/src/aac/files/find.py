"""Module to comb directories and identify AaC files."""
import logging
import os

from aac.parser import parse, ParserError
from aac.files.aac_file import AaCFile


def find_aac_files(root_directory_to_search: str) -> list[str]:
    """Return a list of paths to AaC files in or under the root directory."""
    aac_files = []

    root_dir_abs_path = os.path.abspath(root_directory_to_search)
    if os.path.isdir(root_dir_abs_path):
        directory_results = os.walk(root_dir_abs_path)
        for directory_path, directory_names, filenames in directory_results:
            for filename in filenames:
                filepath = os.path.join(directory_path, filename)
                if is_aac_file(filepath):
                    aac_files.append(AaCFile(filepath, True, False))
    else:
        logging.error(f"Root path '{root_dir_abs_path}' for AaC file discovery is not a directory.")

    return aac_files


def is_aac_file(filepath: str) -> bool:
    """Test if a target file is considered a valid AaC file."""
    filename, file_ext = os.path.splitext(filepath)

    is_valid_aac_file = False
    if file_ext == ".yaml" or file_ext == ".aac":
        try:
            parse(filepath)
        except ParserError as error:
            logging.info(f"File '{filepath}' is not a valid AaC file. Reason: {error.errors}")
        except Exception as error:
            logging.info(f"File '{filepath}' is could not be parsed. Reason: {error}")
        else:
            is_valid_aac_file = True

    return is_valid_aac_file
