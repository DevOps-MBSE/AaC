from unittest import TestCase

from importlib import resources

from aac import package_resources
from aac.lang.constants import DEFINITION_NAME_MODEL, DEFINITION_NAME_SCHEMA
from aac.spec.core import CORE_SPEC_FILE_NAME


class TestPackageResources(TestCase):
    def test_package_resource_imports_core_spec(self):

        expected_file_content = ""
        with resources.open_text("aac.spec", CORE_SPEC_FILE_NAME) as resource_file:
            expected_file_content = resource_file.read()

        actual_file_content = package_resources.get_resource_file_contents("aac.spec", CORE_SPEC_FILE_NAME)

        self.assertEqual(expected_file_content, actual_file_content)

        # Sanity check that there is expected content
        self.assertIn(f"name: {DEFINITION_NAME_SCHEMA}", expected_file_content)
        self.assertIn(f"name: {DEFINITION_NAME_MODEL}", expected_file_content)
