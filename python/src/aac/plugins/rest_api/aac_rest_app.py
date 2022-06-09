"""Module for configuring and maintaining the restful application and its routes."""
from fastapi import FastAPI, HTTPException

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.plugins.rest_api.definition_model import DefinitionModel

app = FastAPI()

active_context = get_active_context()

@app.get("/files", status_code=200)
def get_files():
    """Return a list of all files contributing definitions to the active context."""
    file_names = [definition.source_uri for definition in active_context.definitions]
    return {"files": set(file_names)}


@app.get("/definitions", status_code=200, response_model=list[DefinitionModel])
def get_definitions():
    """Return a list of the definitions in the active context."""
    return {"definitions": active_context.definitions}


@app.get("/definitions/{definition_name}", status_code=200, response_model=DefinitionModel)
def get_definition_by_name(definition_name):
    """Returns a definition from active context by name, or 404 not found if the definition doesn't exist."""
    definition = active_context.get_definition_by_name(definition_name)

    if definition:
        return {"definitions": [definition]}
    else:
        raise HTTPException(status_code=404, detail=f"Definition {definition_name} not found in the context.")


@app.post("/definitions", status_code=201)
def add_definitions():
    """Add a list of definitions to the active context."""

    return {"definitions": active_context.definitions}
