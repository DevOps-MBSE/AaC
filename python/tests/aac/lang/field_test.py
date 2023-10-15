# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

import unittest
from copy import deepcopy
from aac.lang.field import Field


class FieldTestHelper:
    @staticmethod
    def generate_data() -> dict:
        return {
            "name": "test",
            "type": "test",
            "description": "test",
            "is_required": True,
            "default": "test",
        }

    @staticmethod
    def generate_data_required_only() -> dict:
        return {
            "name": "test",
            "type": "test",
        }


class TestField(unittest.TestCase):
    def test_field_from_dict_all_fields(self):
        field_dict = FieldTestHelper.generate_data()
        instance = Field.from_dict(deepcopy(field_dict))
        self.assertEqual(instance.name, field_dict["name"])
        self.assertEqual(instance.type, field_dict["type"])
        self.assertEqual(instance.description, field_dict["description"])
        self.assertEqual(instance.is_required, field_dict["is_required"])
        self.assertEqual(instance.default, field_dict["default"])

        field_dict = FieldTestHelper.generate_data_required_only()
        instance = Field.from_dict(deepcopy(field_dict))
        self.assertEqual(instance.name, field_dict["name"])
        self.assertEqual(instance.type, field_dict["type"])


if __name__ == "__main__":
    unittest.main()