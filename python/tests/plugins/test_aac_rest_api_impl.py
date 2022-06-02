from unittest import TestCase

import json
from fastapi.testclient import TestClient

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.rest_api.aac_rest_app import app


class TestAacRestApi(TestCase):
    test_client = TestClient(app)

    def test_rest_api_get_files(self):
        active_context = get_active_context()
        expected_filenames = list({definition.source_uri for definition in active_context.definitions})

        response = self.test_client.get("/files")
        actual_response = response.json().get("files")
        self.assertEqual(200, response.status_code)
        self.assertListEqual(expected_filenames, actual_response)
