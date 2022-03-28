from typing import Callable

def check_generated_file_contents(path: str, checker: Callable, *args, **kwargs):
    """Check the contents of the provided file at path according to checker.

    Args:
        path (str): The file path whose contents will be checked.
        checker (Callable): A function that checks the file contents appropriately. The first
                            argument will be the file contents.
        *args: Any extra arguments to pass to the checker.
        **kwargs: Any extra keyword arguments to pass to the checker.

    Returns:
        If checker returns anything, return that. Otherwise, returns None.
    """
    with open(path) as generated_file:
        return checker(generated_file.read(), *args, **kwargs)
