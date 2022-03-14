"""Arch-as-Code helper utilities to simplify development.

The aac.util module provides some functionality discovered to be valuable
during the development of aac.  By placing this behavior in a utility
module we prevent code duplication and simplify maintenance.

Avoid adding to this module, always look for ways move these functions into modules with similar functionality.
"""

from contextlib import contextmanager
from os import chdir, getcwd


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
