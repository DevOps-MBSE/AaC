"""Module for configuring and maintaining the restful application and its routes."""
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from http import HTTPStatus
import yaml

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.plugins.rest_api.models.definition_model import DefinitionModel, to_definition_class, to_definition_model
from aac.plugins.rest_api.models.file_model import FileModel, to_file_model

app = FastAPI()


@app.get("/files", status_code=HTTPStatus.OK, response_model=list[FileModel])
def get_files():
    """Return a list of all files contributing definitions to the active context."""
    return [to_file_model(file) for file in get_active_context().get_files_in_context()]


@app.get("/file", status_code=HTTPStatus.OK, response_model=FileModel)
def get_file_by_uri(file_uri: str):
    """Return the target file from the workspace, or HTTPStatus.NOT_FOUND if the file isn't in the context."""
    file_in_context = get_active_context().get_file_in_context_by_uri(file_uri)

    if file_in_context:
        file_model = to_file_model(file_in_context)
        with open(file_in_context.uri) as file:
            file_model.content = file.read()

        return file_model
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"File {file_uri} not found in the context.")


@app.delete("/files", status_code=HTTPStatus.NO_CONTENT)
def remove_files(file_uris: list[str]):
    """Remove the request file(s) and it's associated definitions from the active context."""
    active_context = get_active_context()

    definitions_to_remove = []
    for file_uri in file_uris:
        discovered_definitions = active_context.get_definitions_by_file_uri(file_uri)
        definitions_to_remove.extend(discovered_definitions)

        if len(discovered_definitions) == 0:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"No definition(s) from {file_uri} were found in the context; Will not remove any definitions or files from the context.",
            )

    active_context.remove_definitions_from_context(definitions_to_remove)


@app.get("/definitions", status_code=HTTPStatus.OK, response_model=list[DefinitionModel])
def get_definitions():
    """Return a list of the definitions in the active context."""
    definition_models = [to_definition_model(definition) for definition in get_active_context().definitions]
    return definition_models


@app.get("/definition", status_code=HTTPStatus.OK, response_model=DefinitionModel)
def get_definition_by_name(name: str):
    """Returns a definition from active context by name, or HTTPStatus.NOT_FOUND not found if the definition doesn't exist."""
    definition = get_active_context().get_definition_by_name(name)

    if not definition:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Definition {name} not found in the context.")

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

    discovered_definitions = _get_definitions_from_definition_models(definition_models)

    if len(discovered_definitions.missing) > 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Definition(s) {discovered_definitions.missing} not found in the context; failed to update definitions.",
        )
    else:
        active_context.update_definitions_in_context(discovered_definitions.present)


@app.delete("/definitions", status_code=HTTPStatus.NO_CONTENT)
def remove_definitions(definition_models: list[DefinitionModel]):
    """Remove the request body definitions from the active context."""
    active_context = get_active_context()

    discovered_definitions = _get_definitions_from_definition_models(definition_models)

    if len(discovered_definitions.missing) > 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Definition(s) {discovered_definitions.missing} not found in the context; failed to delete definitions.",
        )
    else:
        active_context.remove_definitions_from_context(discovered_definitions.present)


@dataclass
class _DiscoveredDefinitions:
    present: list[Definition]
    missing: list[str]


def _get_definitions_from_definition_models(definition_models: list[DefinitionModel]) -> _DiscoveredDefinitions:
    """Returns two lists in a tuple, one with definitions found in the context and one with missing definition names."""
    active_context = get_active_context()

    present_definitions = []
    missing_definitions = []
    for model in definition_models:
        old_definition = active_context.get_definition_by_name(model.name)

        if old_definition:
            new_content = yaml.dump(model.structure, sort_keys=False)
            present_definitions.append(Definition(model.name, new_content, old_definition.source.uri, [], model.structure))
        else:
            missing_definitions.append(model.name)

    return _DiscoveredDefinitions(present_definitions, missing_definitions)
