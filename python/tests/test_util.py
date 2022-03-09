"""
Unit tests for the aac.util module.
"""

from os import getcwd
from unittest import TestCase
from tempfile import TemporaryDirectory
from aac import util


class TestArchUtil(TestCase):
    """
    Unit test class for aac.util module.
    """

    def test_new_working_dir(self):
        """
        Unit test for the util.new_working_dir method.
        """
        original_working_directory = getcwd()

        with TemporaryDirectory() as temp_directory, util.new_working_dir(temp_directory):
            self.assertNotEqual(original_working_directory, temp_directory)
            self.assertEqual(getcwd(), temp_directory)
