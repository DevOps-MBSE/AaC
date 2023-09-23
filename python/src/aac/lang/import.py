from dataclasses import dataclass
from attr import attrib, validators
import attr
from aac.cli.aac_execution_result import LanguageError

@dataclass(frozen=True)
class Import():

    files: list[str] = attrib(init=attr.ib(), validator=validators.optional(validators.instance_of(list)))

    # def __init__(self, *args, **kwargs):
    #     if not kwargs or len(kwargs) == 0:
    #         raise LanguageError("Import must be initialized with keyword arguments")
        
    #     if "structure" in kwargs:
    #         structure = kwargs["structure"]
    #         if "files" in structure:
    #             self.files = structure["files"]
    #         else:
    #             raise LanguageError("Import must have files")
    #     else:
    #         if "files" not in kwargs:
    #             raise LanguageError("Import must have files")
    #         else:
    #             self.files = kwargs["files"]
    