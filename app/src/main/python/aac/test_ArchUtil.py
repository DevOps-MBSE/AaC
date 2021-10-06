import unittest
from aac import ArchUtil

class TestArchUtil(unittest.TestCase):

    def test_get_primitive(self):
        expected_results = ["int", "number", "string", "bool", "file", "date"]

        result = ArchUtil.getPrimitives()

        self.assertCountEqual(result, expected_results)

if __name__ == '__main__':
    unittest.main()