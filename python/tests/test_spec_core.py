from unittest import TestCase

from aac.spec import core


class TestSpecCore(TestCase):
    def test_get_primitive(self):
        """
        Unit test for the core.get_primitive method.
        """
        expected_results = ["int", "number", "string", "bool", "file", "date", "map"]

        result = core.get_primitives()

        self.assertCountEqual(result, expected_results)

    def test_get_root_names(self):
        """
        Unit test for the core.get_root_names method.
        """
        expected_results = ["import", "enum", "data", "model", "usecase", "ext", "validation"]

        result = core.get_roots()

        self.assertCountEqual(result, expected_results)

    def test_get_aac_spec(self):
        """
        Unit test for the core.get_aac_spec method.
        """

        aac_data, _ = core.get_aac_spec()

        self.assertGreater(len(aac_data.keys()), 0)
        self.assertGreater(len(aac_data.keys()), 0)

    def test_get_aac_spec_as_yaml(self):
        """
        Unit test for the core.get_aac_spec_as_yaml method.
        """

        aac_yaml = core.get_aac_spec_as_yaml()
        self.assertGreater(len(aac_yaml), 0)
        self.assertGreaterEqual(aac_yaml.count("---"), 14)  # there are 14 base types
