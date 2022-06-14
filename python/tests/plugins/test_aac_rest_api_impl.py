from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from http import HTTPStatus
from unittest import TestCase
import json

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.rest_api.aac_rest_app import app
from aac.plugins.rest_api.definition_model import to_definition_model
from aac.spec import get_aac_spec

from tests.helpers.parsed_definitions import create_behavior_entry, create_model_definition, create_enum_definition


class TestAacRestApi(TestCase):
    test_client = TestClient(app)

    def setUp(self):
        get_active_context(reload_context=True)

    def test_get_files(self):
        active_context = get_active_context()
        expected_filenames = list({definition.source_uri for definition in active_context.definitions})

        response = self.test_client.get("/files")
        actual_response = response.json().get("files")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertListEqual(expected_filenames, actual_response)

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
            self.assertEqual(definition.source_uri, response_definition[0].get("source_uri"))

    def test_get_definition_by_name(self):
        definitions_to_lookup = get_aac_spec()
        successfully_found_definitions = []

        for definition in definitions_to_lookup:
            response = self.test_client.get(f"/definitions/{definition.name}")
            actual_response = response.json()
            expected_response = jsonable_encoder(to_definition_model(definition))
            self.assertEqual(HTTPStatus.OK, response.status_code)
            self.assertEqual(expected_response.get("name"), actual_response.get("name"))
            self.assertEqual(expected_response.get("source_uri"), actual_response.get("source_uri"))
            successfully_found_definitions.append(actual_response)

        self.assertEqual(len(successfully_found_definitions), len(definitions_to_lookup))

    def test_get_definition_by_name_not_found(self):
        fake_definition_name = "FakeModel"

        response = self.test_client.get(f"/definitions/{fake_definition_name}")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    def test_add_definitions(self):
        active_context = get_active_context()
        initial_active_context_count = len(active_context.definitions)

        test_model_definition = create_model_definition("Model")
        test_enum_definition = create_enum_definition("SomeEnum", ["v1", "v2"])
        test_definitions = [test_model_definition, test_enum_definition]

        test_models = [to_definition_model(definition) for definition in test_definitions]

        request_data = [jsonable_encoder(model) for model in test_models]
        response = self.test_client.post("/definitions", data=json.dumps(request_data))
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        post_active_context_count = len(active_context.definitions)
        self.assertEqual(initial_active_context_count + 2, post_active_context_count)

    def test_update_definitions(self):
        test_context = get_active_context()

        test_enum_definition_name = "TestEnum"
        test_enum_definition = create_enum_definition(test_enum_definition_name, ["v1", "v2"])

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)
        test_definitions = [test_model_definition, test_enum_definition]

        test_context.add_definitions_to_context(test_definitions)

        # Update the test definitions
        test_behavior_name = "TestBehavior"
        test_definitions[0].structure["model"]["behavior"] = create_behavior_entry(test_behavior_name)
        additional_enum_value = "v3"
        test_definitions[1].structure["enum"]["values"].append(additional_enum_value)

        request_definition_models = [to_definition_model(definition) for definition in test_definitions]

        request_data = [jsonable_encoder(model) for model in request_definition_models]
        response = self.test_client.put("/definitions", data=json.dumps(request_data))

        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        updated_definitions = [test_context.get_definition_by_name(definition.name) for definition in test_definitions]

        self.assertIn(test_behavior_name, updated_definitions[0].to_yaml())
        self.assertIn(additional_enum_value, updated_definitions[1].to_yaml())

    def test_update_definitions_not_found(self):
        test_enum_definition_name = "TestEnum"
        test_enum_definition = create_enum_definition(test_enum_definition_name, ["v1", "v2"])

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)
        test_definitions = [test_model_definition, test_enum_definition]

        request_definition_models = [to_definition_model(definition) for definition in test_definitions]
        request_data = [jsonable_encoder(model) for model in request_definition_models]
        response = self.test_client.put("/definitions", data=json.dumps(request_data))

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertIn(test_enum_definition_name, response.text)
        self.assertIn(test_model_definition_name, response.text)

    def test_delete_definitions(self):
        test_context = get_active_context()

        test_enum_definition_name = "TestEnum"
        test_enum_definition = create_enum_definition(test_enum_definition_name, ["v1", "v2"])

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)
        test_definitions = [test_model_definition, test_enum_definition]

        test_context.add_definitions_to_context(test_definitions)

        request_definition_models = [to_definition_model(definition) for definition in test_definitions]
        request_data = [jsonable_encoder(model) for model in request_definition_models]
        response = self.test_client.delete("/definitions", data=json.dumps(request_data))

        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        removed_definitions = [test_context.get_definition_by_name(definition.name) for definition in test_definitions]

        self.assertIsNone(removed_definitions[0])
        self.assertIsNone(removed_definitions[1])

    def test_delete_definitions_not_found(self):
        test_enum_definition_name = "TestEnum"
        test_enum_definition = create_enum_definition(test_enum_definition_name, ["v1", "v2"])

        test_model_definition_name = "TestModel"
        test_model_definition = create_model_definition(test_model_definition_name)
        test_definitions = [test_model_definition, test_enum_definition]

        request_definition_models = [to_definition_model(definition) for definition in test_definitions]
        request_data = [jsonable_encoder(model) for model in request_definition_models]
        response = self.test_client.delete("/definitions", data=json.dumps(request_data))

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
