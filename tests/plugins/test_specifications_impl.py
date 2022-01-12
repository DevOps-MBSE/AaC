from unittest import TestCase
from tempfile import NamedTemporaryFile

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.specifications.specifications_impl import spec_validate


class TestSpecifications(TestCase):
    def test_spec_validate(self):
        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(VALID_SPEC)
            temp_spec.seek(0)

            result = spec_validate(temp_spec.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_spec_validate_fails_with_missing_requirement(self):
        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(INVALID_SPEC_MISSING_REQ_ID)
            temp_spec.seek(0)

            result = spec_validate(temp_spec.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.PLUGIN_FAILURE)
            self.assertIn("Invalid requirement id 'SUB-3'", "\n".join(result.messages))


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
