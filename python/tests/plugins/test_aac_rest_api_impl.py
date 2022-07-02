from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from http import HTTPStatus
import json

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.rest_api.aac_rest_app import app
from aac.plugins.rest_api.models.definition_model import to_definition_model
from aac.plugins.rest_api.models.file_model import to_file_model
from aac.spec import get_aac_spec

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import create_behavior_entry, create_model_definition, create_enum_definition


class TestAacRestApi(ActiveContextTestCase):
    test_client = TestClient(app)

    def test_get_files_in_context(self):
        active_context = get_active_context()
        expected_result = [to_file_model(file) for file in active_context.get_files_in_context()]

        response = self.test_client.get("/files/context")
        actual_result = response.json()
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertListEqual(expected_result, actual_result)

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
            successfully_found_definitions.append(actual_response)

        self.assertEqual(len(successfully_found_definitions), len(definitions_to_lookup))

    def test_get_definition_by_name_not_found(self):
        fake_definition_name = "FakeModel"

        response = self.test_client.get(f"/definition/{fake_definition_name}")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_add_definition(self):
        active_context = get_active_context()
        initial_active_context_count = len(active_context.definitions)

        test_enum_definition = create_enum_definition("SomeEnum", ["v1", "v2"])

        response = self.test_client.post("/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_enum_definition))))
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        post_active_context_count = len(active_context.definitions)
        self.assertEqual(initial_active_context_count + 1, post_active_context_count)

    def test_update_definitions(self):
        test_context = get_active_context()

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)

        test_context.add_definition_to_context(test_model_definition)

        # Update the test definitions
        test_behavior_name = "TestBehavior"
        test_model_definition.structure["model"]["behavior"] = create_behavior_entry(test_behavior_name)

        response = self.test_client.put("/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_model_definition))))

        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        updated_definition = test_context.get_definition_by_name(test_model_definition.name)

        self.assertIn(test_behavior_name, updated_definition.to_yaml())

    def test_update_definitions_not_found(self):
        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)

        response = self.test_client.put("/definition", data=json.dumps(jsonable_encoder(to_definition_model(test_model_definition))))

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
