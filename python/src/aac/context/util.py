"""Common utility functions for the context package."""
from aac.context.language_error import LanguageError


def get_python_module_name(package_name: str) -> str:
    """Returns a Python module name, with underscores, from a given package name, which may contain dashes and spaces."""
    if not package_name or package_name == "":
        # we just using default if no package is declared...which really shouldn't happen in core AaC
        return "default"
    result = package_name.replace(" ", "_").replace("-", "_").lower()
    for item in result.split("."):  # expect name to be dot notation
        if not item[0].isalpha():
            raise LanguageError(f"Invalid AaC name: '{item}' within '{package_name}', the first character must be a letter", "Unknown location")
        for sub_item in item.split("_"):  # and name elements may contain _
            if not sub_item.isalnum():  # but things between underscore must be alphanumeric
                raise LanguageError(f"Invalid AaC package name: '{package_name}', the name must be alphanumeric", "Unknown location")
    return result


def get_python_class_name(name: str) -> str:
    """Returns a Python class name from a given name, which may contain dashes and underscores."""
    if not name or name == "":
        raise LanguageError(f"Invalid AaC package name: '{name}', the name must not be empty", "Unknown location")
    if not name[0].isalpha():
        raise LanguageError(f"Invalid AaC name: '{name}', the first character must be a letter", "Unknown location")
    result = name.replace("-", " ").replace("_", " ").replace(" ", "")
    if not result.isalnum():
        raise LanguageError(f"Invalid AaC name: '{name}', the name must be alphanumeric", "Unknown location")
    return result


def get_fully_qualified_name(package_name: str, class_name: str) -> str:
    """Returns the fully qualified name of a class, given the package name and class name."""
    return f"{get_python_module_name(package_name)}.{get_python_class_name(class_name)}"
