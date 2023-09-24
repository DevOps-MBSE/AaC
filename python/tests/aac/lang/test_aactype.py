import unittest
from aac.lang.aactype import AacType

class AaCSubclass(AacType):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

class TestAACType(unittest.TestCase):
    def test_aactype(self):
        aac_type = AaCSubclass("my_type", "My type")
        self.assertEqual(aac_type.name, "my_type")
        self.assertEqual(aac_type.description, "My type")

if __name__ == '__main__':
    unittest.main()