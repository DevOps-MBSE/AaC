"""Pydantic Version of the AaC Definition Class."""

from pydantic import BaseModel

from aac.lang.definitions.definition import Definition


class DefinitionModel(BaseModel):
    name: str
    content: str
    source_uri: str
    structure: dict


def to_definition_model(definition: Definition) -> DefinitionModel:
    """ """
    return DefinitionModel(
        name=definition.name,
        content=definition.content,
        source_uri=definition.source_uri,
        structure=definition.structure
    )
