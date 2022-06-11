"""Pydantic Version of the AaC Definition Class."""

from pydantic import BaseModel

from aac.lang.definitions.definition import Definition


class DefinitionModel(BaseModel):
    """REST API Model for the Definition class."""
    name: str
    content: str
    source_uri: str
    structure: dict


def to_definition_model(definition: Definition) -> DefinitionModel:
    """Return a DefinitionModel representation from a Definition object."""
    return DefinitionModel(
        name=definition.name,
        content=definition.content,
        source_uri=definition.source_uri,
        structure=definition.structure
    )


def to_definition_class(definition_model: DefinitionModel) -> Definition:
    """Return a Definition object from a DefinitionModel object."""
    definition = Definition(
        name=definition_model.name,
        content="",
        source_uri="",
        structure=definition_model.structure
    )
    definition.content = definition.to_yaml()
    return definition
