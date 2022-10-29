"""Provides a simple struct for tracking which component is managing which workspace file."""

from attr import attrib, attrs, validators


@attrs
class ManagedWorkspaceFile:
    """
    Provides a simple struct for tracking which component is managing which workspace file.

    Attributes:
        file_uri (str): The file URI
        is_client_managed (bool): True if the file is managed by the LSP client, false otherwise
    """

    file_uri: str = attrib(validator=validators.instance_of(str))
    is_client_managed: bool = attrib(default=False, validator=validators.instance_of(bool))
