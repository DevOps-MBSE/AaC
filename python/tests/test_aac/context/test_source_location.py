from unittest import TestCase
from aac.context.source_location import SourceLocation


class TestSourceLocation(TestCase):
    def test_source_location(self):
        loc = SourceLocation(1, 2, 3, 4)
        
        self.assertTrue(isinstance(loc.to_tuple(), tuple))
