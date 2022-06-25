"""Pydantic Version of the AaC Definition Class."""
from typing import Optional
from pydantic import BaseModel

from aac.files.aac_file import AaCFile


class FileModel(BaseModel):
    """REST API Model for the Definition class."""
    uri: str
    content: Optional[str] = ""
    is_user_editable: bool
    is_loaded_in_context: bool


def to_file_model(file: AaCFile, file_content: str = "") -> FileModel:
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
