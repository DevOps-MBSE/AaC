from aac.spec import core

from tests.active_context_test_case import ActiveContextTestCase

EXPECTED_ROOT_KEY_NAMES = ["import", "enum", "schema", "map", "model", "usecase", "ext", "validation", "spec"]


class TestSpecCore(ActiveContextTestCase):
    def test_get_primitive(self):
        """
        Unit test for the core.get_primitive method.
        """
        expected_results = ["int", "number", "string", "bool", "file", "directory", "date", "reference"]

        result = core.get_primitives()

        self.assertCountEqual(result, expected_results)

    def test_get_root_keys(self):
        """
        Unit test for the core.get_root_keys method.
        """
        result = core.get_root_keys()

        self.assertListEqual(result, EXPECTED_ROOT_KEY_NAMES)

    def test_get_root_fields(self):
        """
        Unit test for the core.get_root_fields method.
        """
        result = core.get_root_fields()

        self.assertEqual(len(result), len(EXPECTED_ROOT_KEY_NAMES))
        for field in result:
            self.assertIsNotNone(field.get("name"))
            self.assertIsNotNone(field.get("description"))
            self.assertIn(field.get("name"), EXPECTED_ROOT_KEY_NAMES)

    def test_get_aac_spec(self):
        """
        Unit test for the core.get_aac_spec method.
        """

        aac_definitions = core.get_aac_spec()

        self.assertGreater(len(aac_definitions), 0)

    def test_get_aac_spec_as_yaml(self):
        """
        Unit test for the core.get_aac_spec_as_yaml method.
        """

        aac_yaml = core.get_aac_spec_as_yaml()
        self.assertGreater(len(aac_yaml), 0)
        self.assertGreaterEqual(aac_yaml.count("---"), 14)  # there are 14 base types
