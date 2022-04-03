from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.validate import validate_definitions, ValidationError

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_field_entry,
)


class TestValidators(TestCase):
    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_validate_definitions_with_valid_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_data_definition("Empty Data", [test_field])

        with validate_definitions([test_definition]) as result:
            self.assertTrue(result.is_valid)

    def test_validate_definitions_with_invalid_reference_definition(self):
        test_field = create_field_entry("TestField", "striiiing")
        test_definition = create_data_definition("Empty Data", [test_field])

        with self.assertRaises(ValidationError):
            with validate_definitions([test_definition]):
                pass
