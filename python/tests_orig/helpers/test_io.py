"""
Unit tests for the aac.util module.
"""

from os import getcwd, path, makedirs, removedirs
from unittest import TestCase
from tests.helpers.io import new_working_dir


class TestIOHelpers(TestCase):
    def test_new_working_dir(self):
        original_working_directory = getcwd()
        temp_directory = path.abspath(path.join("tmp", "dir"))
        makedirs(temp_directory)

        try:
            with new_working_dir(temp_directory):
                self.assertNotEqual(getcwd(), original_working_directory)
                self.assertEqual(getcwd(), temp_directory)

            self.assertEqual(getcwd(), original_working_directory)
        finally:
            removedirs(temp_directory)
