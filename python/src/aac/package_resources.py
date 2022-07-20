"""Module that contains helper functions for interacting with package resources."""

from importlib import resources


def get_resource_file_contents(package: str, resource: str) -> str:
    """
    Returns the contents of a package resource as a string.

    Args:
        package (str): the package containing the resource
        resource (str): the resource's filename

    Returns:
        A string containing the entire file content of the package resource.
    """
    with resources.open_text(package, resource) as resource_file:
        return resource_file.read()


def get_resource_file_path(package: str, resource: str) -> str:
    """
    Returns the path to the package resource as a string.

    Args:
        package (str): the package containing the resource
        resource (str): the resource's filename

    Returns:
        A string containing the resource's path.
    """
    with resources.path(package, resource) as path:
        return str(path)
