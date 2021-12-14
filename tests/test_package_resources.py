from unittest import TestCase

from importlib import resources

from aac import package_resources


class TestPackageResources(TestCase):

    def test_package_resource_imports_core_spec(self):

        expected_file_content = ""
        with resources.open_text("aac.spec", "spec.yaml") as resource_file:
            expected_file_content = resource_file.read()

        actual_file_content = package_resources.get_resource_file_contents("aac.spec", "spec.yaml")

        self.assertEqual(expected_file_content, actual_file_content)

        # Sanity check that there is expected content
        self.assertIn("name: root", expected_file_content)
        self.assertIn("name: model", expected_file_content)
