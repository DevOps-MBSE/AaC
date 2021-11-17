"""
Unit tests for the aac.util module.
"""

from unittest import TestCase

from aac import util


class TestArchUtil(TestCase):
    """
    Unit test class for aac.util module.
    """

    def test_get_primitive(self):
        """
        Unit test for the util.get_primitive method.
        """
        expected_results = ["int", "number", "string", "bool", "file", "date", "map"]

        result = util.get_primitives()

        self.assertCountEqual(result, expected_results)

    def test_get_root_names(self):
        """
        Unit test for the util.get_root_names method.
        """
        expected_results = ["import", "enum", "data", "model", "usecase", "ext"]

        result = util.get_roots()

        self.assertCountEqual(result, expected_results)

    def test_get_aac_spec(self):
        """
        Unit test for the util.get_aac_spec method.
        """

        aac_data, _ = util.get_aac_spec()

        self.assertGreater(len(aac_data.keys()), 0)
        self.assertGreater(len(aac_data.keys()), 0)

    def test_get_aac_spec_as_yaml(self):
        """
        Unit test for the util.get_aac_spec_as_yaml method.
        """

        aac_yaml = util.get_aac_spec_as_yaml()
        self.assertGreater(len(aac_yaml), 0)
        self.assertGreaterEqual(aac_yaml.count("---"), 14)  # there are 14 base types

    def test_get_models_by_type(self):
        """
        Unit test for the util.get_models_by_type method.
        """
        aac_data, aac_enums = util.get_aac_spec()
        num_data = len(aac_data)
        num_enums = len(aac_enums)
        num_models = 0
        all_aac = aac_data | aac_enums
        self.assertEqual(len(util.get_models_by_type(all_aac, "data")), num_data)
        self.assertEqual(len(util.get_models_by_type(all_aac, "enum")), num_enums)
        self.assertEqual(len(util.get_models_by_type(all_aac, "model")), num_models)

    def test_search(self):
        """
        Unit test for the util.search method.
        """
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
