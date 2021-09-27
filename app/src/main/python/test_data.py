import unittest

from aac import aac

class TestData(unittest.TestCase):

    def test_simple(self):
        data = aac.Data("test", "value")
        self.assertEqual(data.name, "test")
        self.assertEqual(data.value, "value")

    def test_list(self):
        test_val = ["one", "two", "three"]
        data = aac.Data("test", test_val)
        self.assertEqual(data.name, "test")
        self.assertEqual(data.value, test_val)

    def test_complex_object(self):
        test_val = {"one": "first", "two": "second", "three": "third"}
        data = aac.Data("test", test_val)
        self.assertEqual(data.name, "test")
        self.assertEqual(data.value, test_val)

if __name__ == '__main__':
    unittest.main()