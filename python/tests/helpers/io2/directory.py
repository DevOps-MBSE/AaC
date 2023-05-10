"""Helpers for dealing with directories while testing."""

import os

from contextlib import contextmanager
from typing import Optional


def clear_directory(dirspec: str, file_list: Optional[list[str]] = None, dir_list: Optional[list[str]] = None) -> None:
    """
    Clear the specified directory of any contents.

    WARNING: This makes changes to the user's file system - be sure you know what you're doing, you
    want to do this, and you're only removing generated files.

    It's sometimes useful to make sure a directory is empty before running tests so as to ensure
    file generation, for example, is working consistently and correctly. This utility assists in
    achieving that.

    Arguments:
        dirspec (str): The absolute directory path whose contents will be removed.
        file_list (list[str]): A list of files to be removed from dirspec. If not provided, all
                               files are removed. (optional)
        dir_list (list[str]): A list of subdirectories to be removed from dirspec. If not provided,
                              all subdirectories are removed. (optional)
    """

    def should_remove(pathspec: str, paths_to_remove: Optional[list[str]]):
        return isinstance(pathspec, str) and (paths_to_remove and pathspec in paths_to_remove) or not paths_to_remove

    def remove_file(pathspec: str):
        os.remove(os.path.join(dirspec, pathspec))

    def remove_directory(pathspec: str):
        directory = os.path.join(dirspec, pathspec)
        clear_directory(directory)
        os.rmdir(directory)

    items = os.listdir(dirspec)

    files = filter(lambda pathspec: os.path.isfile(pathspec) and should_remove(pathspec, file_list), items)
    list(map(remove_file, files))

    dirs = filter(lambda pathspec: os.path.isdir(pathspec) and should_remove(pathspec, dir_list), items)
    list(map(remove_directory, dirs))


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
    current_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield os.getcwd()
        os.chdir(current_dir)
    except Exception as e:
        os.chdir(current_dir)
        raise e
