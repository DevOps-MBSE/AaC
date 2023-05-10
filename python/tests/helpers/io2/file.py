"""Helpers for dealing with files while testing."""

import os

from tempfile import NamedTemporaryFile, TemporaryDirectory

from tests.helpers.io2.directory import new_working_dir


def temporary_test_file_wo_cm(content: str, **extra_file_attrs):
    """
    Create a temporary file containing content for testing without the use of a context manager.

    Users are required to clean up the file when they're done with it.

    Arguments:
        content (str): A string to use as the contents of the file.
        extra_file_attrs (dict): Extra file attributes that will be used when creating the test
                                 file. These should be valid parameters to NamedTemporaryFile.
                                 (optional)

            Extra file attributes:
                * mode (default: "w")
                * buffering (default: -1)
                * encoding (default: None)
                * newline (default: None)
                * suffix (default: None)
                * prefix (default: None)
                * dir (default: `TemporaryDirectory()`)

    Returns:
        The temporary test file containing the specified contents.
    """
    directory = extra_file_attrs.get("dir", TemporaryDirectory().name)
    os.makedirs(directory, exist_ok=True)
    mode = extra_file_attrs.get("mode", "w")
    extra_file_attrs |= {"dir": directory, "mode": mode, "delete": False}
    with new_working_dir(directory):
        file = NamedTemporaryFile(**extra_file_attrs)
        file.write(content)
        file.seek(0)

    return file
