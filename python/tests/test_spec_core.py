from aac.lang.spec import (
    get_primitives,
    get_root_keys,
    get_root_fields,
    get_aac_spec,
    get_aac_spec_as_yaml,
)

from tests.active_context_test_case import ActiveContextTestCase

EXPECTED_ROOT_KEY_NAMES = ["import", "enum", "schema", "map", "model", "usecase", "ext", "validation"]


class TestSpecCore(ActiveContextTestCase):
    def test_get_primitive(self):
        """
        Unit test for the core.get_primitive method.
        """
        expected_results = ["int", "number", "string", "bool", "file", "directory", "date", "reference"]

        result = get_primitives()

        self.assertCountEqual(result, expected_results)

    def test_get_root_keys(self):
        """
        Unit test for the core.get_root_keys method.
        """
        result = get_root_keys()

        self.assertListEqual(result, EXPECTED_ROOT_KEY_NAMES)

    def test_get_root_fields(self):
        """
        Unit test for the core.get_root_fields method.
        """
        result = get_root_fields()

        self.assertEqual(len(result), len(EXPECTED_ROOT_KEY_NAMES))
        for field in result:
            self.assertIsNotNone(field.get("name"))
            self.assertIsNotNone(field.get("description"))
            self.assertIn(field.get("name"), EXPECTED_ROOT_KEY_NAMES)

    def test_get_aac_spec(self):
        """
        Unit test for the core.get_aac_spec method.
        """

        aac_definitions = get_aac_spec()

        self.assertGreater(len(aac_definitions), 0)

    def test_get_aac_spec_as_yaml(self):
        """
        Unit test for the core.get_aac_spec_as_yaml method.
        """

        aac_yaml = get_aac_spec_as_yaml()
        self.assertGreater(len(aac_yaml), 0)
        self.assertGreaterEqual(aac_yaml.count("---"), 14)  # there are 14 base types
