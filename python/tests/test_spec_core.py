from aac.lang.constants import (
    PRIMITIVE_TYPE_BOOL,
    PRIMITIVE_TYPE_DATE,
    PRIMITIVE_TYPE_DIRECTORY,
    PRIMITIVE_TYPE_FILE,
    PRIMITIVE_TYPE_INT,
    PRIMITIVE_TYPE_NUMBER,
    PRIMITIVE_TYPE_REFERENCE,
    PRIMITIVE_TYPE_STRING,
    ROOT_KEY_COMMAND_GROUP,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_IMPORT,
    ROOT_KEY_MODEL,
    ROOT_KEY_PLUGIN,
    ROOT_KEY_SCHEMA,
    ROOT_KEY_SPECIFICATION,
    ROOT_KEY_USECASE,
    ROOT_KEY_VALIDATION,
)
from aac.spec import core

from tests.active_context_test_case import ActiveContextTestCase

EXPECTED_ROOT_KEY_NAMES = [
    ROOT_KEY_COMMAND_GROUP,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_IMPORT,
    ROOT_KEY_MODEL,
    ROOT_KEY_PLUGIN,
    ROOT_KEY_SCHEMA,
    ROOT_KEY_SPECIFICATION,
    ROOT_KEY_USECASE,
    ROOT_KEY_VALIDATION,
]


class TestSpecCore(ActiveContextTestCase):
    def test_get_primitive(self):
        """
        Unit test for the core.get_primitive method.
        """
        expected_results = [
            PRIMITIVE_TYPE_BOOL,
            PRIMITIVE_TYPE_DATE,
            PRIMITIVE_TYPE_DIRECTORY,
            PRIMITIVE_TYPE_FILE,
            PRIMITIVE_TYPE_INT,
            PRIMITIVE_TYPE_NUMBER,
            PRIMITIVE_TYPE_REFERENCE,
            PRIMITIVE_TYPE_STRING,
        ]

        result = core.get_primitives()

        # Sort the results
        expected_results.sort()
        result.sort()

        self.assertListEqual(result, expected_results)

    def test_get_root_keys(self):
        """
        Unit test for the core.get_root_keys method.
        """
        result = core.get_root_keys()

        # Sort for comparison
        EXPECTED_ROOT_KEY_NAMES.sort()
        result.sort()

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
