import os

from tempfile import TemporaryDirectory, NamedTemporaryFile
from typing import Optional

from tests.helpers.io2.directory import clear_directory


class TemporaryTestFile:
    def __init__(
        self,
        content: str,
        name: str = "",
        clean_up: bool = True,
        mode: str = "w",
        buffering: int = -1,
        encoding: Optional[str] = None,
        newline: Optional[str] = None,
        suffix: Optional[str] = None,
        prefix: Optional[str] = None,
        dir: Optional[str] = None,
    ):
        """
        Return a TemporaryTestFile context-manager object.

        Arguments:
            content (str): A string to use as the contents of the file.
            name (Optional[str]): An optional name to give to the file. (default: None)
            clean_up (Optional[str]): Whether to clean up the test file/directory after exiting the context manager.
              Recognized Options:
                'all': Remove `dir` along with all files and directories under `dir`. (default)
                'files': Remove all files under `dir` only.
                'directories': Remove all directories under `dir` only.

            The below parameters are the same as those provided to `NamedTemporaryFile`:
              mode (str): The `mode` argument to `NamedTemporaryFile`. (default: "w")
              buffering (int): The `buffering` argument to `NamedTemporaryFile`. (default: -1)
              encoding (Optional[str]): The `encoding` argument to `NamedTemporaryFile`. (default: None)
              newline (Optional[str]): The `newline` argument to `NamedTemporaryFile`. (default: None)
              suffix (Optional[str]): The `suffix` argument to `NamedTemporaryFile`. (default: None)
              prefix (Optional[str]): The `prefix` argument to `NamedTemporaryFile`. (default: None)
              dir (Optional[str]): The `dir` argument to `NamedTemporaryFile`. (default: `TemporaryDirectory()`)
        """
        self.clean_up = clean_up
        self.directory = dir or TemporaryDirectory().name
        self.test_file = NamedTemporaryFile(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=suffix,
            prefix=prefix,
            dir=self.directory,
            delete=False,
        )
        self.__write_content(content)
        self.__maybe_rename_file(name)

    def __write_content(self, content: str):
        self.test_file.write(content)
        self.test_file.seek(0)

    def __maybe_rename_file(self, name: Optional[str] = None):
        self._original_name = self.test_file.name
        if name:
            full_path = os.path.join(self.directory, name)
            os.rename(self.test_file.name, full_path)
            self.test_file.name = full_path

    def __enter__(self):
        """
        Create a temporary file containing content for testing.

        Yields:
            The temporary test file containing the specified contents.
        """
        return self.test_file

    def __exit__(self, *_):
        """Clean the temporary test file."""
        if self.clean_up and os.path.exists(self.directory):
            clear_directory(self.directory)
            os.removedirs(self.directory)
