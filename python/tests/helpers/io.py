"""Helpers for testing.

This module provides helpers for making tests cleaner by abstracting common patterns.
"""

import os

from contextlib import contextmanager
from tempfile import NamedTemporaryFile, TemporaryDirectory


def clear_directory(dirspec: str, *file_list: list[str]) -> None:
    """Clear the specified directory of any file contents.

    WARNING: This makes changes to the user's file system - be sure you know what you're doing, you
    want to do this, and you're only removing generated files.

    It's sometimes useful to make sure a directory is empty before running tests so as to ensure (e.g.) file generation is
    working consistently and correctly. This utility assists in achieving that.

    Arguments:
        dirspec (str): The absolute directory path whose contents will be removed.
        file_list (str): A list of files to be removed from dirspec. If not provided, all files are removed. (optional)

    Returns:
        Nothing
    """

    def should_remove(f):
        return isinstance(f, str) and (file_list and f in file_list) or not file_list

    files = filter(should_remove, os.listdir(dirspec))
    list(map(lambda f: os.remove(f"{dirspec}/{f}"), files))


@contextmanager
def temporary_test_file(content: str, **extra_file_attrs):
    """Create a temporary file containing content for testing.

    Arguments:
        content (str): A string to use as the contents of the file.
        extra_file_attrs (dict): Extra file attributes that will be used when creating the test
                                 file. These should be valid parameters to NamedTemporaryFile.
                                 (optional)

    Yields:
        The temporary test file containing the specified contents.
    """
    with TemporaryDirectory() as temp_dir, NamedTemporaryFile(dir=temp_dir, mode="w", **(extra_file_attrs or {})) as f:
        f.write(content)
        f.seek(0)

        yield f
