from unittest import TestCase
from aac.context.source_location import SourceLocation


class TestSourceLocation(TestCase):
    def test_source_location(self):
        loc = SourceLocation(1, 2, 3, 4)
        self.assertIsInstance(loc.to_tuple(), tuple)

        loc2 = SourceLocation(2, 1, 3, 4)
        self.assertIsInstance(loc2.to_tuple(), tuple)

        loc3 = SourceLocation(1, 2, 4, 3)
        self.assertIsInstance(loc3.to_tuple(), tuple)
        self.assertNotEqual(loc, loc2, loc3)

    def test_source_location_incorrect_type(self):
        with self.assertRaises(TypeError):
            loc = SourceLocation("1", "2", "3", "4")  # noqa: F841
