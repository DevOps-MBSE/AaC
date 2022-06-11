"""Module for configuring and maintaining the restful application and its routes."""
from fastapi import FastAPI, HTTPException
from http import HTTPStatus
import yaml

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.plugins.rest_api.definition_model import DefinitionModel, to_definition_class, to_definition_model

app = FastAPI()


@app.get("/files", status_code=HTTPStatus.OK)
def get_files():
    """Return a list of all files contributing definitions to the active context."""
    file_names = [definition.source_uri for definition in get_active_context().definitions]
    return {"files": set(file_names)}


@app.get("/definitions", status_code=HTTPStatus.OK, response_model=list[DefinitionModel])
def get_definitions():
    """Return a list of the definitions in the active context."""
    definition_models = [to_definition_model(definition) for definition in get_active_context().definitions]
    return definition_models


@app.get("/definitions/{definition_name}", status_code=HTTPStatus.OK, response_model=DefinitionModel)
def get_definition_by_name(definition_name):
    """Returns a definition from active context by name, or HTTPStatus.NOT_FOUND not found if the definition doesn't exist."""
    definition = get_active_context().get_definition_by_name(definition_name)
    if not definition:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Definition {definition_name} not found in the context.")
    else:
        return to_definition_model(definition)


@app.post("/definitions", status_code=HTTPStatus.NO_CONTENT)
def add_definitions(definition_models: list[DefinitionModel]):
    """Add a list of definitions to the active context."""
    definitions = [to_definition_class(model) for model in definition_models]
    get_active_context().add_definitions_to_context(definitions)


@app.put("/definitions", status_code=HTTPStatus.NO_CONTENT)
def update_definitions(definition_models: list[DefinitionModel]) -> None:
    """Update the request body definitions in the active context."""
    active_context = get_active_context()

    updated_definitions = []
    missing_definitions = []
    for model in definition_models:
        old_definition = active_context.get_definition_by_name(model.name)

        if old_definition:
            new_content = yaml.dump(model.structure, sort_keys=False)
            updated_definitions.append(Definition(model.name, new_content, old_definition.source_uri, [], model.structure))
        else:
            missing_definitions.append(model.name)

    if len(missing_definitions) > 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Definition(s) {missing_definitions} not found in the context; failed to update definitions.",
        )
    else:
        active_context.update_definitions_in_context(updated_definitions)


@app.delete("/definitions", status_code=HTTPStatus.NO_CONTENT)
def remove_definitions(definition_models: list[DefinitionModel]):
    """Remove the request body definitions from the active context."""
    active_context = get_active_context()

    definitions_to_remove = []
    missing_definitions = []
    for model in definition_models:
        old_definition = active_context.get_definition_by_name(model.name)

        if old_definition:
            new_content = yaml.dump(model.structure, sort_keys=False)
            definitions_to_remove.append(Definition(model.name, new_content, old_definition.source_uri, [], model.structure))
        else:
            missing_definitions.append(model.name)

    if len(missing_definitions) > 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Definition(s) {missing_definitions} not found in the context; failed to update definitions.",
        )
    else:
        active_context.remove_definitions_from_context(definitions_to_remove)
