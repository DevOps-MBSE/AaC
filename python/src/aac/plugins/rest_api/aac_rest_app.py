"""Module for configuring and maintaining the restful application and its routes."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from http import HTTPStatus
import os
import logging

from aac.io.files.aac_file import AaCFile
from aac.io.files.find import find_aac_files, is_aac_file
from aac.io.paths import sanitize_filesystem_path
from aac.io.parser import parse
from aac.io.writer import write_definitions_to_file
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.rest_api.models.definition_model import DefinitionModel, to_definition_class, to_definition_model
from aac.plugins.rest_api.models.file_model import FileModel, FilePathModel, FilePathRenameModel, to_file_model

app = FastAPI()

AVAILABLE_AAC_FILES: list[AaCFile] = []
WORKSPACE_DIR: str = os.getcwd()


# File CRUD Operations

@app.get("/files/context", status_code=HTTPStatus.OK, response_model=list[FileModel])
def get_files_from_context():
    """Return a list of all files contributing definitions to the active context."""
    return [to_file_model(file) for file in get_active_context().get_files_in_context()]


@app.get("/files/available", status_code=HTTPStatus.OK, response_model=list[FileModel])
def get_available_files(background_tasks: BackgroundTasks):
    """Return a list of all files available in the workspace for import into the active context. The list of files returned does not include files already in the context."""
    # Update the files via an async function so that any changes to the files shows up, eventually.
    background_tasks.add_task(refresh_available_files_in_workspace)

    #  Having to use a cached response for now as the file-walking makes the response take too long.
    return [to_file_model(file) for file in AVAILABLE_AAC_FILES]


@app.get("/file", status_code=HTTPStatus.OK, response_model=FileModel)
def get_file_by_uri(uri: str):
    """Return the target file from the workspace, or HTTPStatus.NOT_FOUND if the file isn't in the context."""
    file_in_context = get_active_context().get_file_in_context_by_uri(uri)

    if file_in_context:
        file_model = to_file_model(file_in_context)
        with open(file_in_context.uri) as file:
            file_model.content = file.read()

        return file_model
    else:
        _report_error_response(HTTPStatus.NOT_FOUND, f"File {uri} not found in the context.")


@app.post("/files/import", status_code=HTTPStatus.NO_CONTENT)
def import_files_to_context(file_models: list[FilePathModel]):
    """Import the list of files into the context."""
    files_to_import = set([str(model.uri) for model in file_models])
    valid_aac_files = set(filter(is_aac_file, files_to_import))
    invalid_files = files_to_import.difference(valid_aac_files)

    if len(invalid_files) > 0:
        _report_error_response(HTTPStatus.BAD_REQUEST, f"Invalid files were asked to imported. Invalid files: {invalid_files}.")
    else:
        new_file_definitions = [parse(file) for file in valid_aac_files]
        list(map(get_active_context().add_definitions_to_context, new_file_definitions))


@app.put("/file", status_code=HTTPStatus.NO_CONTENT)
def rename_file_uri(rename_request: FilePathRenameModel) -> None:
    """Update a file's uri. (Rename file)."""
    active_context = get_active_context()
    current_file_path = sanitize_filesystem_path(str(rename_request.current_file_uri))
    new_file_path = sanitize_filesystem_path(rename_request.new_file_uri)

    file_in_context = active_context.get_file_in_context_by_uri(current_file_path)

    if not _is_file_path_in_working_directory(new_file_path):
        _report_error_response(HTTPStatus.BAD_REQUEST, f"Files can only be renamed to a uri inside of the working directory: {WORKSPACE_DIR}.")

    if file_in_context:
        os.rename(current_file_path, new_file_path)
        definitions_to_update = active_context.get_definitions_by_file_uri(current_file_path)
        for definition in definitions_to_update:
            definition.source.uri = new_file_path

    else:
        _report_error_response(HTTPStatus.NOT_FOUND, f"File {current_file_path} not found in the context.")


@app.delete("/file", status_code=HTTPStatus.NO_CONTENT)
def remove_file_by_uri(uri: str):
    """Remove the requested file and it's associated definitions from the active context."""
    active_context = get_active_context()

    file_in_context = active_context.get_file_in_context_by_uri(uri)
    if not file_in_context:
        _report_error_response(HTTPStatus.NOT_FOUND, f"File {uri} not found in the context.")

    definitions_to_remove = []
    discovered_definitions = active_context.get_definitions_by_file_uri(uri)
    definitions_to_remove.extend(discovered_definitions)

    if len(discovered_definitions) == 0:
        _report_error_response(HTTPStatus.NOT_FOUND, f"No definition(s) from {uri} were found in the context; Will not remove any definitions or files from the context.")

    active_context.remove_definitions_from_context(definitions_to_remove)


# Definition CRUD Operations

@app.get("/definitions", status_code=HTTPStatus.OK, response_model=list[DefinitionModel])
def get_definitions():
    """Return a list of the definitions in the active context."""
    definition_models = [to_definition_model(definition) for definition in get_active_context().definitions]
    return definition_models


@app.get("/definition", status_code=HTTPStatus.OK, response_model=DefinitionModel)
def get_definition_by_name(name: str):
    """
    Returns a definition from active context by name, or HTTPStatus.NOT_FOUND not found if the definition doesn't exist.

    Returns:
        200 HTTPStatus.OK if successful.
    """
    definition = get_active_context().get_definition_by_name(name)

    if not definition:
        _report_error_response(HTTPStatus.NOT_FOUND, f"Definition {name} not found in the context.")
    else:
        return to_definition_model(definition)


@app.post("/definition", status_code=HTTPStatus.NO_CONTENT)
def add_definition(definition_model: DefinitionModel):
    """
    Add the definition to the active context. If the definition's source file doesn't exist, a new one will be created.

    Args:
        definition_model (DefinitionModel): The definition model in request body.

    Returns:
        204 HTTPStatus.NO_CONTENT if successful.
    """
    definition_source_uri = definition_model.source_uri

    if not _is_file_path_in_working_directory(definition_source_uri):
        _report_error_response(HTTPStatus.BAD_REQUEST, f"Definition can't be added to a file {definition_source_uri} which is outside of the working directory: {WORKSPACE_DIR}.")

    definition_to_write = to_definition_class(definition_model)
    active_context = get_active_context()
    existing_definitions = active_context.get_definitions_by_file_uri(definition_source_uri)

    is_user_editable = True
    if len(existing_definitions) > 0:
        is_user_editable = existing_definitions[0].source.is_user_editable

    if not is_user_editable:
        _report_error_response(HTTPStatus.BAD_REQUEST, f"File {definition_source_uri} can't be edited by users.")

    write_definitions_to_file([definition_to_write, *existing_definitions], definition_source_uri, is_user_editable)
    updated_definition_source_and_lexemes = parse(definition_source_uri)
    active_context.add_definition_to_context(definition_to_write)
    active_context.update_definitions_in_context(updated_definition_source_and_lexemes)


@app.put("/definition", status_code=HTTPStatus.NO_CONTENT)
def update_definition(definition_model: DefinitionModel) -> None:
    """Update the request body definitions in the active context."""
    active_context = get_active_context()

    definition_to_update = active_context.get_definition_by_name(definition_model.name)

    if definition_to_update:
        active_context.update_definition_in_context(to_definition_class(definition_model))
    else:
        _report_error_response(HTTPStatus.NOT_FOUND, f"Definition(s) {definition_model.name} not found in the context; failed to update definitions.")


@app.delete("/definition", status_code=HTTPStatus.NO_CONTENT)
def remove_definition_by_name(name: str):
    """Remove the definition via name from the active context."""
    active_context = get_active_context()

    definition_to_remove = active_context.get_definition_by_name(name)

    if definition_to_remove:
        active_context.remove_definition_from_context(definition_to_remove)
    else:
        _report_error_response(HTTPStatus.NOT_FOUND, f"Definition {name} not found in the context; failed to delete definitions.")


def _get_available_files_in_workspace() -> set[AaCFile]:
    """Get the available AaC files in the workspace sans files already in the context."""
    active_context = get_active_context()
    aac_files_in_context = set(active_context.get_files_in_context())
    aac_files_in_workspace = set(find_aac_files(WORKSPACE_DIR))

    return aac_files_in_workspace.difference(aac_files_in_context)


async def refresh_available_files_in_workspace() -> None:
    """Used to refresh the available files. Used in async since it takes too long for being used in request-response flow."""
    global AVAILABLE_AAC_FILES
    AVAILABLE_AAC_FILES = list(_get_available_files_in_workspace())


def _report_error_response(code: HTTPStatus, error: str):
    logging.error(error)
    raise HTTPException(
        status_code=code,
        detail=error,
    )


def _is_file_path_in_working_directory(file_path: str) -> bool:
    return str(file_path).startswith(WORKSPACE_DIR)
