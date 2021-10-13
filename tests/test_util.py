"""
Unit tests for the aac.util module.
"""

from unittest import TestCase
from aac import util


class TestArchUtil(TestCase):
    def test_get_primitive(self):
        expected_results = ["int", "number", "string", "bool", "file", "date", "map"]

        result = util.get_primitives()

        self.assertCountEqual(result, expected_results)

    def test_get_root_names(self):
        expected_results = ["import", "enum", "data", "model", "usecase", "ext"]

        result = util.get_roots()

        self.assertCountEqual(result, expected_results)

    def test_getAaCSpec(self):

        aac_data, _ = util.get_aac_spec()

        self.assertTrue(len(aac_data.keys()) > 0)
        self.assertTrue(len(aac_data.keys()) > 0)

    def test_search(self):

        data_entry = {
            "data": {
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "type", "type": "BehaviorType"},
                    {"name": "description", "type": "string"},
                    {"name": "tags", "type": "string[]"},
                    {"name": "input", "type": "Field[]"},
                    {"name": "output", "type": "Field[]"},
                    {"name": "acceptance", "type": "Scenario[]"},
                ],
                "name": "Behavior",
                "required": ["name", "type", "acceptance"],
            }
        }

        expected = [
            "string",
            "BehaviorType",
            "string",
            "string[]",
            "Field[]",
            "Field[]",
            "Scenario[]",
        ]
        data_model_types = util.search(data_entry, ["data", "fields", "type"])

        self.assertCountEqual(data_model_types, expected)
