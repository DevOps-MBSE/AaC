from nose2.tools import params
from unittest import TestCase

from aac.io.paths import sanitize_filesystem_path


class TestPaths(TestCase):

    @params(
        ("/workspace/AaC/python/src/aac/test.py", "/workspace/AaC/python/src/aac/test.py"),
        ("/workspace/AaC/../AaC/python/src/aac/test.py", "/workspace/AaC/python/src/aac/test.py"),
        ("src/aac/test.py", "/workspace/AaC/python/src/aac/test.py"),
        ("../../src/aac/test.py", "/workspace/src/aac/test.py"),
        ("/workspace/AaC/python/src/aac/../../../../test.py", "/workspace/test.py"),
        ("/workspace/AaC/python/src/aac/test.exe%00.py", "/workspace/AaC/python/src/aac/test.exe.py"),
        ("/workspace/%2e%2e%2fAaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/%2e%2e/AaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/..%2fAaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/%2e%2e%5cAaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/%2e%2e\AaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/..%5c\AaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/%252e%252e%255c\AaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
        ("/workspace/..%255c\AaC/python/src/aac/test.py", "/AaC/python/src/aac/test.py"),
    )
    def test_sanitize_filesystem_path(self, test_path: str, expected_result: str):
        self.assertEqual(sanitize_filesystem_path(test_path), expected_result)
