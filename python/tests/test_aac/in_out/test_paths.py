import os
from parameterized import parameterized
from unittest import TestCase
from aac.in_out.paths import sanitize_filesystem_path

WORKING_TEST_DIR = os.getcwd()

def _get_working_directory_parent_directory(level_of_directories_up: int = 1) -> str:
    """Get the n-level parent directory from the WORKING_TEST_DIR. Useful for testing '../' in paths."""
    path_to_return = WORKING_TEST_DIR
    for i in range(0, level_of_directories_up):
        new_path = os.path.dirname(path_to_return)
        if new_path != path_to_return:
            path_to_return = new_path
        else:
            break

    return path_to_return

class TestPaths(TestCase):
    # Success test block happy path cases
    @parameterized.expand([
        [f"{WORKING_TEST_DIR}/src/aac/test.py",                     f"{WORKING_TEST_DIR}/src/aac/test.py",],
        [f"{WORKING_TEST_DIR}/../src/aac/test.py",                  f"{os.path.dirname(WORKING_TEST_DIR)}/src/aac/test.py"],
        ["src/aac/test.py",                                         f"{WORKING_TEST_DIR}/src/aac/test.py"],
        ["../../src/aac/test.py",                                   f"{_get_working_directory_parent_directory(2)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/../../src/aac/test.py",               f"{_get_working_directory_parent_directory(2)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/src/aac/test.exe%00.py",              f"{WORKING_TEST_DIR}/src/aac/test.exe.py"],
        [f"{WORKING_TEST_DIR}/%2e%2e%2f/src/aac/test.py",           f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/%2e%2e//src/aac/test.py",             f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/..%2f/src/aac/test.py",               f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/%2e%2e%5c/src/aac/test.py",           f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/%2e%2e\/src/aac/test.py",             f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/..%5c\/src/aac/test.py",              f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/%252e%252e%255c\/src/aac/test.py",    f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
        [f"{WORKING_TEST_DIR}/..%255c\/src/aac/test.py",            f"{_get_working_directory_parent_directory(1)}/src/aac/test.py"],
    ])
    def test_sequence_success(self, test_path, expected_result):
        self.assertEqual(sanitize_filesystem_path(test_path), expected_result)

    # Expected fail test block for sad path cases
    @parameterized.expand([
        [f"{WORKING_TEST_DIR}/src/aac/AAA.py",                      f"{WORKING_TEST_DIR}/src/aac/BBB.py"],  # Example of input for a fail-test
        [f"{WORKING_TEST_DIR}/src/aac/AAA.py",                      f""],  # Empty directory
        [f"{WORKING_TEST_DIR}/src/aac/AAA.py",                      f"{WORKING_TEST_DIR}/src/aac//AAA.py"],  # Double forward slash test
        [f" ",                                                      f""],  # Space vs empty/null directory
        [f" ",                                                      f" "],  # Tab vs space directory
        [f"{WORKING_TEST_DIR}/src/aac/AAA.py",                      f"{WORKING_TEST_DIR}/src/aac/AAA.py "],  # Trailing space test
        ])
    def test_sequence_fail(self, test_path, expected_result):
        self.assertNotEqual(sanitize_filesystem_path(test_path), expected_result)  # Example of a fail-test assertNotEqual rather than assertEqual

