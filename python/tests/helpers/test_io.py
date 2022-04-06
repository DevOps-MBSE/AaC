"""
Unit tests for the aac.util module.
"""

from os import getcwd
from unittest import TestCase
from tempfile import TemporaryDirectory
from unittest.case import skip
from tests.helpers.io import new_working_dir


class TestIOHelpers(TestCase):
    @skip("temporarily skip")
    def test_new_working_dir(self):
        original_working_directory = getcwd()

        with TemporaryDirectory() as temp_directory, new_working_dir(temp_directory):
            self.assertNotEqual(original_working_directory, temp_directory)
            self.assertEqual(getcwd(), temp_directory)
        self.assertEqual(getcwd(), original_working_directory)
