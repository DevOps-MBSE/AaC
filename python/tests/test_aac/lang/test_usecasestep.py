# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

import unittest
from copy import deepcopy
from aac.lang.usecasestep import UsecaseStep

TEST_DATA_ALL = {
    "name": "test",
    "source": "test",
    "target": "test",
    "action": "test",
    "condition": [
        {"condition": "test", "steps": ["test", "test"]},
        {"condition": "test", "steps": ["test", "test"]},
    ],
    "loop": {"condition": "test", "steps": ["test", "test"]},
}

TEST_DATA_REQUIRED = {"name": "test"}


class TestUsecaseStep(unittest.TestCase):
    def test_usecasestep_from_dict_all_fields(self):
        usecasestep_dict = TEST_DATA_ALL
        instance = UsecaseStep.from_dict(deepcopy(usecasestep_dict))
        self.assertEqual(instance.name, usecasestep_dict["name"])
        self.assertEqual(instance.source, usecasestep_dict["source"])
        self.assertEqual(instance.target, usecasestep_dict["target"])
        self.assertEqual(instance.action, usecasestep_dict["action"])
        self.assertIsNotNone(instance.condition)
        self.assertIsNotNone(instance.loop)

        usecasestep_dict = TEST_DATA_REQUIRED
        instance = UsecaseStep.from_dict(deepcopy(usecasestep_dict))
        self.assertEqual(instance.name, usecasestep_dict["name"])


if __name__ == "__main__":
    unittest.main()
