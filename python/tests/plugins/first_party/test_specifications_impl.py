from tempfile import TemporaryDirectory

import os

from aac.plugins.first_party.specifications.specifications_impl import spec_csv

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_success
from tests.helpers.io import TemporaryTestFile


class TestSpecifications(ActiveContextTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def test_spec_csv(self):

        with TemporaryDirectory() as temp_dir, TemporaryTestFile(VALID_SPEC) as temp_arch_file:
            result = spec_csv(temp_arch_file.name, temp_dir)
            assert_plugin_success(result)

            # Assert each spec has its own file.
            generated_file_names = os.listdir(temp_dir)
            self.assertEqual(2, len(generated_file_names))

            self.assertIn("Subsystem.csv", generated_file_names)
            self.assertIn("Module.csv", generated_file_names)

            # Assert Subsystem.csv contents
            with open(os.path.join(temp_dir, "Subsystem.csv")) as subsystem_csv_file:
                subsystem_csv_contents = subsystem_csv_file.read()
                subsystem_csv_contents = subsystem_csv_contents.replace("\"", "")  # it's not clear what does and doesn't get quoted by the CSV writer, so eliminate quotes
                # Assert csv contents are present
                self.assertIn('Spec Name,Section,ID,Requirement,Parents,Children', subsystem_csv_contents)
                self.assertIn('Subsystem,,SUB-1,When receiving a message, the subsystem shall respond with a value.,,', subsystem_csv_contents)
                self.assertIn('Subsystem,Other Requirements,SUB-2,Do things.,,', subsystem_csv_contents)

            # Assert Module.csv contents
            with open(os.path.join(temp_dir, "Module.csv")) as module_csv_file:
                module_csv_contents = module_csv_file.read()
                module_csv_contents = module_csv_contents.replace("\"", "")  # it's not clear what does and doesn't get quoted by the CSV writer, so eliminate quotes
                # Assert csv contents are present
                self.assertIn('Spec Name,Section,ID,Requirement,Parents,Children', module_csv_contents)
                self.assertIn('Module,,MOD-1,When receiving a message, the module shall respond with a value.,SUB-1,', module_csv_contents)
                self.assertIn('Module,,MOD-2,When receiving a message do things.,SUB-2,', module_csv_contents)


VALID_SPEC = """
spec:
  name: Subsystem
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: "SUB-1"
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test

  sections:
    - name: Other Requirements
      description:  Other requirements.
      requirements:
        - id: "SUB-2"
          shall: Do things.
---
spec:
  name: Module
  description:  This is a representative module requirement specification.
  requirements:
    - id: "MOD-1"
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        ids:
          - "SUB-1"
      attributes:
        - name: TADI
          value: Test
    - id: "MOD-2"
      shall:  When receiving a message do things.
      parent:
        ids:
          - "SUB-2"
      attributes:
        - name: TADI
          value: Test
"""

INVALID_SPEC_MISSING_REQ_ID = """
spec:
  name: Subsystem
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: "SUB-1"
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test

  sections:
    - name: Other Requirements
      description:  Other requirements.
      requirements:
        - id: "SUB-2"
          shall: Do things.
---
spec:
  name: Module
  description:  This is a representative module requirement specification.
  requirements:
    - id: "MOD-1"
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        ids:
          - "SUB-3"
      attributes:
        - name: TADI
          value: Test
    - id: "MOD-2"
      shall:  When receiving a message do things.
      parent:
        ids:
          - "SUB-2"
      attributes:
        - name: TADI
          value: Test
"""
