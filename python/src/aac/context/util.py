from aac.context.language_error import LanguageError

def get_python_module_name(package_name: str) -> str:
    if not package_name or package_name == "":
        # we're just using default if no package is declared...which really shouldn't happen in the base AaC stuff
        return "default"
    result = package_name.replace(" ", "_").replace("-", "_").lower()
    for item in result.split("."): # expect name to be dot notation
        if not item[0].isalpha():
            raise LanguageError(f"Invalid name for creation of python module name: '{item}' within '{package_name}', the first character must be a letter")
        for sub_item in item.split("_"): # and name elements may contain _
            if not sub_item.isalnum(): # but things between underscore must be alphanumeric
                raise LanguageError(f"Invalid AaC package name for creation of python module name: '{package.name}', the name must be alphanumeric")
    return result
    
def get_python_class_name(name: str) -> str:
    if not name or name == "":
        raise LanguageError(f"Invalid name for creation of python class name: '{name}', the name must be alphanumeric")
    if not name[0].isalpha():
        raise LanguageError(f"Invalid name for creation of python class name: '{name}', the first character must be a letter")
    result =  name.replace("-", " ").replace("_", " ").replace(" ", "")
    if not result.isalnum():
        raise LanguageError(f"Invalid name for creation of python class name: '{name}', the name must be alphanumeric", None)
    return result

def get_fully_qualified_name(package_name: str, class_name: str) -> str:
    return f"{get_python_module_name(package_name)}.{get_python_class_name(class_name)}"