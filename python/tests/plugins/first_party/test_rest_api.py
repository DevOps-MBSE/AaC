import json
import os
import asyncio

from tempfile import TemporaryDirectory
from unittest.mock import patch
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from http import HTTPStatus

from aac.io.constants import YAML_DOCUMENT_EXTENSION, AAC_DOCUMENT_EXTENSION
from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.json_schema import get_definition_json_schema
from aac.plugins.plugin_manager import get_plugin_commands
from aac.plugins.first_party.rest_api.aac_rest_app import app, refresh_available_files_in_workspace
from aac.plugins.first_party.rest_api.models.command_model import CommandRequestModel
from aac.plugins.first_party.rest_api.models.definition_model import to_definition_model
from aac.plugins.first_party.rest_api.models.file_model import FilePathModel, FilePathRenameModel, to_file_model
from aac.spec import get_aac_spec
from aac.spec.core import _get_aac_spec_file_path

from tests.helpers.io import temporary_test_file
from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_model_definition,
    create_enum_definition,
    create_schema_definition,
)


class TestAacRestApiCommandEndpoints(ActiveContextTestCase):
    test_client = TestClient(app)

    def test_get_available_commands(self):
        excluded_rest_api_commands = ["rest-api", "start-lsp-io", "start-lsp-tcp"]
        expected_result = list(filter(lambda command: command.name not in excluded_rest_api_commands, get_plugin_commands()))
        expected_commands_dict = {command.name: command for command in expected_result}

        response = self.test_client.get("/commands")
        actual_result = response.json()

        actual_commands_dict = {command.get("name"): command for command in actual_result}

        self.assertEqual(HTTPStatus.OK, response.status_code)

        for command_name, command in expected_commands_dict.items():
            actual_command = actual_commands_dict.get(command_name)
            self.assertIsNotNone(actual_command)
            self.assertEqual(command.description, actual_command.get("description"))

            actual_command_arguments_dict = {arg.get("name"): arg for arg in actual_command.get("arguments")}
            for argument in command.arguments:
                actual_argument = actual_command_arguments_dict.get(argument.name)
                self.assertIsNotNone(actual_argument)
                self.assertEqual(argument.description, actual_argument.get("description"))
                self.assertEqual(argument.data_type, actual_argument.get("data_type"))

    def test_execute_validate_command(self):
        command_name = "validate"
        test_model = create_model_definition("Model")

        with temporary_test_file(test_model.to_yaml()) as temp_file:
            request_arguments = CommandRequestModel(name=command_name, arguments=[temp_file.name])
            response = self.test_client.post("/command", data=json.dumps(jsonable_encoder(request_arguments)))

            self.assertEqual(HTTPStatus.OK, response.status_code)
            self.assertTrue(response.json().get("success"))
            self.assertIn("success", response.text)
            self.assertIn(command_name, response.text)
            self.assertIn(temp_file.name, response.text)

    def test_execute_puml_component_command(self):
        command_name = "puml-component"
        test_model_name = "Model"
        test_model = create_model_definition(test_model_name)

        with temporary_test_file(test_model.to_yaml()) as temp_file:
            temp_directory = os.path.dirname(temp_file.name)
            self.assertEqual(len(os.listdir(temp_directory)), 1)

            request_arguments = CommandRequestModel(name=command_name, arguments=[temp_file.name, temp_directory])
            response = self.test_client.post("/command", data=json.dumps(jsonable_encoder(request_arguments)))

            component_directory = os.path.join(temp_directory, "component")

            self.assertEqual(HTTPStatus.OK, response.status_code)
            self.assertTrue(response.json().get("success"))
            self.assertIn("success", response.text)
            self.assertIn(temp_directory, response.text)
            self.assertEqual(len(os.listdir(temp_directory)), 2)
            self.assertIn("component", os.listdir(temp_directory))
            self.assertEqual(len(os.listdir(component_directory)), 1)
            self.assertIn(f"{os.path.basename(temp_file.name)}_{test_model_name.lower()}.puml", os.listdir(component_directory))

    def test_execute_rest_api_command_fails(self):
        command_name = "rest-api"
        request_arguments = CommandRequestModel(name=command_name, arguments=[])
        response = self.test_client.post("/command", data=json.dumps(jsonable_encoder(request_arguments)))

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)


class TestAacRestApiFileEndpoints(ActiveContextTestCase):
    test_client = TestClient(app)

    def test_get_files_in_context(self):
        active_context = get_active_context()
        expected_result = [to_file_model(file) for file in active_context.get_files_in_context()]

        response = self.test_client.get("/files/context")
        actual_result = response.json()
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertListEqual(expected_result, actual_result)

    def test_get_available_aac_files(self):
        test_model_definition = create_model_definition("TestModel")
        test_enum_definition = create_enum_definition("TestEnum", [])
        test_schema_definition = create_schema_definition("TestSchema")

        file1_content = f"{test_model_definition.to_yaml()}---\n{test_enum_definition.to_yaml()}"
        file2_content = test_schema_definition.to_yaml()

        with TemporaryDirectory() as temp_directory:

            patch_manager = patch("aac.plugins.first_party.rest_api.aac_rest_app.WORKSPACE_DIR", temp_directory)
            file1_manager = temporary_test_file(file1_content, dir=temp_directory, suffix=YAML_DOCUMENT_EXTENSION)
            file2_manager = temporary_test_file(file2_content, dir=temp_directory, suffix=AAC_DOCUMENT_EXTENSION)

            with patch_manager, file1_manager as temp_file1, file2_manager as temp_file2:

                # Force the server to refresh the available files now that the working dir is altered.
                asyncio.run(refresh_available_files_in_workspace())

                response = self.test_client.get("/files/available")
                actual_result = response.json()
                self.assertEqual(HTTPStatus.OK, response.status_code)
                actual_result_files_name = [file.get("uri") for file in actual_result]
                self.assertIn(temp_file1.name, actual_result_files_name)
                self.assertIn(temp_file2.name, actual_result_files_name)

    def test_get_file_in_context_by_uri(self):
        core_spec_uri = _get_aac_spec_file_path()

        response = self.test_client.get(f"/file?uri={core_spec_uri}")
        actual_result = response.json()
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(core_spec_uri, actual_result.get("uri"))
        self.assertFalse(actual_result.get("is_user_editable"))

    def test_import_file_to_context_by_uri(self):
        active_context = get_active_context()

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)

        file_content = test_model_definition.to_yaml()

        with TemporaryDirectory() as temp_directory:

            patch_manager = patch("aac.plugins.first_party.rest_api.aac_rest_app.WORKSPACE_DIR", temp_directory)
            file_manager = temporary_test_file(file_content, dir=temp_directory, suffix=YAML_DOCUMENT_EXTENSION)
            with patch_manager, file_manager as temp_file:
                file_path_model = FilePathModel(uri=temp_file.name)

                self.assertIsNone(active_context.get_definition_by_name(test_model_definition_name))

                response = self.test_client.post("/files/import", data=json.dumps(jsonable_encoder([file_path_model])))
                self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

                self.assertIsNotNone(active_context.get_definition_by_name(test_model_definition_name))

    def test_rename_file_in_context(self):
        active_context = get_active_context()

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)
        file_content = test_model_definition.to_yaml()

        with TemporaryDirectory() as temp_dir:
            old_file_name = "OldTestFile.yaml"
            new_file_name = "TestFile.aac"
            new_file_uri = os.path.join(temp_dir, new_file_name)

            temp_file = open(os.path.join(temp_dir, old_file_name), "w")
            temp_file.writelines(file_content)
            temp_file.close()

            with patch("aac.plugins.first_party.rest_api.aac_rest_app.WORKSPACE_DIR", temp_dir):
                parsed_definition = parse(temp_file.name)
                active_context.add_definitions_to_context(parsed_definition)

                rename_request_data = FilePathRenameModel(current_file_uri=temp_file.name, new_file_uri=new_file_uri)
                response = self.test_client.put("/file", data=json.dumps(jsonable_encoder(rename_request_data)))
                self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

                file_names_in_context = [file.uri for file in active_context.get_files_in_context()]
                self.assertIn(new_file_uri, file_names_in_context)

            # Clean-up the renamed file.
            os.remove(new_file_uri)

    def test_remove_file_from_context(self):
        active_context = get_active_context()

        core_spec_path = _get_aac_spec_file_path()
        core_definitions = get_aac_spec()

        response = self.test_client.delete(f"/file?uri={core_spec_path}")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        self.assertGreater(len(core_definitions), 0)
        for core_definition in core_definitions:
            self.assertIsNone(active_context.get_definition_by_name(core_definition.name))


class TestAacRestApiDefinitionEndpoints(ActiveContextTestCase):
    test_client = TestClient(app)

    def test_get_definitions(self):
        self.maxDiff = None
        active_context = get_active_context()

        response = self.test_client.get("/definitions")
        actual_response = response.json()

        expected_definition_names = [definition.name for definition in active_context.definitions]
        actual_definition_names = [model.get("name") for model in actual_response]

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertListEqual(expected_definition_names, actual_definition_names)
        for definition in active_context.definitions:
            response_definition = [def_model for def_model in actual_response if def_model.get("name") == definition.name]
            self.assertEqual(definition.name, response_definition[0].get("name"))
            self.assertEqual(definition.source.uri, response_definition[0].get("source_uri"))

    def test_get_definition_by_name(self):
        definitions_to_lookup = get_aac_spec()
        successfully_found_definitions = []

        for definition in definitions_to_lookup:
            response = self.test_client.get(f"/definition?name={definition.name}")
            actual_response = response.json()
            expected_response = jsonable_encoder(to_definition_model(definition))
            self.assertEqual(HTTPStatus.OK, response.status_code)
            self.assertEqual(expected_response.get("name"), actual_response.get("name"))
            self.assertEqual(expected_response.get("source_uri"), actual_response.get("source_uri"))
            self.assertIsNone(actual_response.get("json_schema"))
            successfully_found_definitions.append(actual_response)

        self.assertEqual(len(successfully_found_definitions), len(definitions_to_lookup))

    def test_get_definition_by_name_with_schema(self):
        active_context = get_active_context()
        definition_to_lookup = get_aac_spec()[0]
        successfully_found_definitions = []

        response = self.test_client.get(f"/definition?name={definition_to_lookup.name}&include_json_schema=True")
        actual_response = response.json()
        expected_response = jsonable_encoder(to_definition_model(definition_to_lookup))
        expected_response["json_schema"] = get_definition_json_schema(definition_to_lookup, active_context)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected_response.get("name"), actual_response.get("name"))
        self.assertEqual(expected_response.get("source_uri"), actual_response.get("source_uri"))
        self.assertIsNotNone(actual_response.get("json_schema"))
        self.assertEqual(expected_response.get("json_schema"), actual_response.get("json_schema"))
        successfully_found_definitions.append(actual_response)

    def test_get_definition_by_name_not_found(self):
        fake_definition_name = "FakeModel"

        response = self.test_client.get(f"/definition/{fake_definition_name}")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_add_definition(self):
        active_context = get_active_context()
        test_enum_definition = create_enum_definition("SomeEnum", ["v1", "v2"])

        # Establish an existing test user file in the context
        with temporary_test_file(test_enum_definition.to_yaml()) as aac_file:
            with patch("aac.plugins.first_party.rest_api.aac_rest_app.WORKSPACE_DIR", os.path.dirname(aac_file.name)):
                parsed_test_enum_definition = parse(aac_file.name)
                active_context.add_definitions_to_context(parsed_test_enum_definition)

                # Add our actual test content
                test_model_definition = create_model_definition("SomeModel")
                test_model_definition.source = parsed_test_enum_definition[0].source

                response = self.test_client.post(
                    "/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_model_definition)))
                )
                self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
                self.assertIsNotNone(active_context.get_definition_by_name(test_model_definition.name))

    def test_add_definition_create_source_file(self):
        active_context = get_active_context()

        test_enum_definition = create_enum_definition("SomeEnum", ["v1", "v2"])

        with TemporaryDirectory() as temp_directory:
            with patch("aac.plugins.first_party.rest_api.aac_rest_app.WORKSPACE_DIR", temp_directory):
                source_file_name = "test_source.aac"
                source_file = f"{temp_directory}/{source_file_name}"
                self.assertFalse(os.path.exists(source_file))
                test_enum_definition.source.uri = source_file

                response = self.test_client.post(
                    "/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_enum_definition)))
                )

                self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
                self.assertTrue(os.path.exists(source_file))
                self.assertIsNotNone(active_context.get_definition_by_name(test_enum_definition.name))

                with open(source_file) as source_file:
                    self.assertEqual(source_file.read(), test_enum_definition.to_yaml())

    def test_add_definition_create_source_file_outside_workspace_fails(self):
        active_context = get_active_context()

        test_enum_definition = create_enum_definition("SomeEnum", ["v1", "v2"])

        # Demonstrate that users can't write content to files outside of the designated workspace.
        with TemporaryDirectory() as temp_directory:
            source_file_name = "test_source.aac"
            source_file = f"{temp_directory}{source_file_name}"
            self.assertFalse(os.path.exists(source_file))
            test_enum_definition.source.uri = source_file

            response = self.test_client.post(
                "/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_enum_definition)))
            )

            self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)
            self.assertIn("outside of the working directory", response.text)
            self.assertIn(source_file, response.text)
            self.assertFalse(os.path.exists(source_file))
            self.assertIsNone(active_context.get_definition_by_name(test_enum_definition.name))

    def test_add_definition_fails_to_edit_safe_file(self):
        active_context = get_active_context(True)
        core_spec_path = _get_aac_spec_file_path()
        test_source = active_context.get_file_in_context_by_uri(core_spec_path)

        self.assertIsNotNone(
            test_source,
            f"Couldn't find the core spec by uri {core_spec_path}. Expected uri is: {get_aac_spec()[0].source.uri}",
        )

        test_enum_definition = create_enum_definition("SomeEnum", ["v1", "v2"])
        test_enum_definition.source = test_source

        response = self.test_client.post(
            "/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_enum_definition)))
        )
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)
        self.assertIn("can't be edited", response.text)
        self.assertIn(test_source.uri, response.text)

    def test_update_definitions(self):
        test_context = get_active_context()

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)

        test_context.add_definition_to_context(test_model_definition)

        # Update the test definitions
        test_behavior_name = "TestBehavior"
        test_model_definition.structure["model"]["behavior"] = [create_behavior_entry(test_behavior_name)]

        response = self.test_client.put(
            "/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_model_definition)))
        )

        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        updated_definition = test_context.get_definition_by_name(test_model_definition.name)

        self.assertIn(test_behavior_name, updated_definition.to_yaml())

    def test_update_definitions_not_found(self):
        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)

        response = self.test_client.put(
            "/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_model_definition)))
        )

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertIn(test_model_definition_name, response.text)

    def test_delete_definitions(self):
        test_context = get_active_context()

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)

        test_context.add_definition_to_context(test_model_definition)

        response = self.test_client.delete(f"/definition?name={test_model_definition_name}")

        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        removed_definition = test_context.get_definition_by_name(test_model_definition_name)

        self.assertIsNone(removed_definition)

    def test_delete_definitions_not_found(self):
        test_model_definition_name = "TestModel"

        response = self.test_client.delete(f"/definition?name={test_model_definition_name}")

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
