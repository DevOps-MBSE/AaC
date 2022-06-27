"""Module for configuring and maintaining the restful application and its routes."""
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, BackgroundTasks
from http import HTTPStatus
import asyncio
import yaml
import os
import logging

from aac.files.aac_file import AaCFile
from aac.files.find import find_aac_files, is_aac_file
from aac.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.plugins.rest_api.models.definition_model import DefinitionModel, to_definition_class, to_definition_model
from aac.plugins.rest_api.models.file_model import FileModel, FilePathModel, to_file_model

app = FastAPI()

AVAILABLE_AAC_FILES = []


@app.get("/files/context", status_code=HTTPStatus.OK, response_model=list[FileModel])
def get_files_in_context():
    """Return a list of all files contributing definitions to the active context."""
    return [to_file_model(file) for file in get_active_context().get_files_in_context()]


@app.get("/files/available", status_code=HTTPStatus.OK, response_model=list[FileModel])
def get_available_files(background_tasks: BackgroundTasks):
    """Return a list of all files available in the workspace for import into the active context. The list of files returned does not include files already in the context."""
    # Update the files via an async function so that any changes to the files shows up, eventually.
    background_tasks.add_task(_refresh_available_files_in_workspace)

    #  Having to use a cached response for now as the file-walking makes the response take about 5 seconds, which is too long.
    return [to_file_model(file) for file in AVAILABLE_AAC_FILES]


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


@app.post("/files/import", status_code=HTTPStatus.NO_CONTENT)
def import_files_to_context(file_models: list[FilePathModel]):
    """Import the list of files into the context."""
    files_to_import = set([str(model.uri) for model in file_models])
    valid_aac_files = set(filter(is_aac_file, files_to_import))
    invalid_files = files_to_import.difference(valid_aac_files)

    if len(invalid_files) > 0:
        error_message = f"Invalid files were asked to imported. Invalid files: {invalid_files}"
        logging.error(error_message)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=error_message,
        )
    else:
        new_file_definitions = [parse(file) for file in valid_aac_files]
        list(map(get_active_context().add_definitions_to_context, new_file_definitions))


@app.delete("/files", status_code=HTTPStatus.NO_CONTENT)
def remove_files(file_uris: list[FilePathModel]):
    """Remove the request file(s) and it's associated definitions from the active context."""
    active_context = get_active_context()

    definitions_to_remove = []
    for file_uri in file_uris:
        discovered_definitions = active_context.get_definitions_by_file_uri(str(file_uri.uri))
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
            present_definitions.append(Definition(model.name, new_content, old_definition.source, [], model.structure))
        else:
            missing_definitions.append(model.name)

    return _DiscoveredDefinitions(present_definitions, missing_definitions)


def _get_available_files_in_workspace() -> set[AaCFile]:
    """Get the available AaC files in the workspace sans files already in the context."""
    active_context = get_active_context()
    aac_files_in_context = set(active_context.get_files_in_context())
    aac_files_in_workspace = set(find_aac_files(os.getcwd()))

    return aac_files_in_workspace.difference(aac_files_in_context)


async def _refresh_available_files_in_workspace() -> None:
    """Used to refresh the available files. Used in async since it takes too long for being used in request-response flow."""
    global AVAILABLE_AAC_FILES
    AVAILABLE_AAC_FILES = list(_get_available_files_in_workspace())

# Initialize AVAILABLE_AAC_FILES by calling the refresh function after the function declaration.
asyncio.run(_refresh_available_files_in_workspace())
