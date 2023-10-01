import unittest
from aac.lang.overwriteoption import OverwriteOption

class TestOverwriteOption(unittest.TestCase):

    def test_overwriteoption_from_dict(self):

        self.assertEqual(OverwriteOption.from_dict('OVERWRITE'), OverwriteOption.OVERWRITE)
        self.assertEqual(OverwriteOption.from_dict('SKIP'), OverwriteOption.SKIP)
        
        with self.assertRaises(ValueError):
            OverwriteOption.from_dict('NEVER_GONNA_BE_A_VALID_ENUM_VALUE')

if __name__ == '__main__':
    unittest.main()