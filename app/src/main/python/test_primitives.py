import unittest
from aac import aac

class TestData(unittest.TestCase):

    def test_primitive(self):
        # this is pretty dumb...not sure unit testing an enum makes sense
        print(aac.Primitives.INT)
        int_type = aac.Primitives.INT
        self.assertEqual("INT", int_type.name)
        num_type = aac.Primitives.NUMBER
        self.assertEqual("NUMBER", num_type.name)
        bool_type = aac.Primitives.BOOL
        self.assertEqual("BOOL", bool_type.name)
        string_type = aac.Primitives.STRING
        self.assertEqual("STRING", string_type.name)
        file_type = aac.Primitives.FILE
        self.assertEqual("FILE", file_type.name)
        date_type = aac.Primitives.DATE
        self.assertEqual("DATE", date_type.name)
        object_type = aac.Primitives.OBJECT
        self.assertEqual("OBJECT", object_type.name)

if __name__ == '__main__':
    unittest.main()