from unittest import TestCase

from importlib import resources

from aac import package_resources
from aac.lang.spec import CORE_SPEC_FILE_NAME


class TestPackageResources(TestCase):

    def test_package_resource_imports_core_spec(self):

        expected_file_content = ""
        with resources.open_text("aac.lang.spec", CORE_SPEC_FILE_NAME) as resource_file:
            expected_file_content = resource_file.read()

        actual_file_content = package_resources.get_resource_file_contents("aac.lang.spec", CORE_SPEC_FILE_NAME)

        self.assertEqual(expected_file_content, actual_file_content)

        # Sanity check that there is expected content
        self.assertIn("name: root", expected_file_content)
        self.assertIn("name: model", expected_file_content)
