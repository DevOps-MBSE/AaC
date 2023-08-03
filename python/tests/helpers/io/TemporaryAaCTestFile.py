from typing import Optional
from aac.io.constants import AAC_DOCUMENT_EXTENSION
from tests.helpers.io import TemporaryTestFile, CleanUpOption


class TemporaryAaCTestFile(TemporaryTestFile):
    def __init__(
        self,
        content: str,
        name: str = "",
        clean_up: CleanUpOption = CleanUpOption.ALL,
        mode: str = "w",
        buffering: int = -1,
        encoding: Optional[str] = None,
        newline: Optional[str] = None,
        prefix: Optional[str] = None,
        dir: Optional[str] = None,
    ):
        """
        Return a TemporaryAaCTestFile context-manager object.

        This test file is almost equivalent to TemporaryTestFile class, but the .aac extension is automatically applied.

        Arguments:
            content (str): A string to use as the contents of the file.
            name (str): An optional name to give to the file. (default: "")
            clean_up (CleanUpOption): Whether to clean up the test file/directory after exiting the context manager.
              Recognized Options:
                ALL: Remove `dir` along with all files and directories under `dir`. (default)
                FILES: Remove all files under `dir` only.
                DIRECTORIES: Remove all directories under `dir` only.
                NONE: Do not remove any files/directories under `dir`.

            The below parameters are the same as those provided to `NamedTemporaryFile`:
              mode (str): The `mode` argument to `NamedTemporaryFile`. (default: "w")
              buffering (int): The `buffering` argument to `NamedTemporaryFile`. (default: -1)
              encoding (Optional[str]): The `encoding` argument to `NamedTemporaryFile`. (default: None)
              newline (Optional[str]): The `newline` argument to `NamedTemporaryFile`. (default: None)
              prefix (Optional[str]): The `prefix` argument to `NamedTemporaryFile`. (default: None)
              dir (Optional[str]): The `dir` argument to `NamedTemporaryFile`. (default: `TemporaryDirectory()`)
        """
        super().__init__(
            content=content,
            name=name,
            clean_up=clean_up,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=AAC_DOCUMENT_EXTENSION,
            prefix=prefix,
            dir=dir
        )
