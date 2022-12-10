"""Pydantic Version of the AaC Definition Class."""
from typing import Optional
from pydantic import BaseModel, FilePath

from aac.io.files.aac_file import AaCFile


class FileModel(BaseModel):
    """REST API Model for the File class."""
    uri: str
    content: Optional[str]
    is_user_editable: bool
    is_loaded_in_context: bool


class FilePathModel(BaseModel):
    """REST API Model for just file uris."""
    uri: FilePath


class FilePathRenameModel(BaseModel):
    """REST API Model for renaming a file."""
    current_file_uri: FilePath
    new_file_uri: str


def to_file_model(file: AaCFile, file_content: Optional[str] = None) -> FileModel:
    """
    Return a FileModel representation from an AaCFile object.

    Args:
        file (AaCFile): The AaCFile object to convert
        file_content (str): The content of the file -- this information is not stored in AaCFile

    Returns:
        A FileModel for use in the REST API.
    """
    return FileModel(
        uri=file.uri, content=file_content, is_user_editable=file.is_user_editable, is_loaded_in_context=file.is_loaded_in_context
    )


def to_file_class(file: FileModel) -> AaCFile:
    """
    Return an AacFile object from a FileModel object.

    Args:
        file (FileModel): The FileModel object to convert

    Returns:
        An AaCFile object.
    """
    return AaCFile(
        uri=file.uri, is_user_editable=file.is_user_editable, is_loaded_in_context=file.is_loaded_in_context
    )
