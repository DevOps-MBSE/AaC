from unittest import TestCase
from tempfile import NamedTemporaryFile

from aac.plugins.specifications.specifications_impl import spec_validate, AacSpecValidationException


class TestSpecifications(TestCase):

    def test_spec_validate(self):

        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(VALID_SPEC)
            temp_spec.seek(0)

            try:
                spec_validate(temp_spec.name)
            except AacSpecValidationException as e:
                self.fail("validate() raised AacSpecValidationException with error: {0}".format(e))

    def test_spec_validate_fails_with_missing_abbrv(self):

        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(INVALID_SPEC_MISSING_ABRV)
            temp_spec.seek(0)

            with self.assertRaises(AacSpecValidationException) as context_manager:
                spec_validate(temp_spec.name)

                validation_exception = context_manager.exception
                self.assertIn("Spec name Subsystem must have 1 abbrv", validation_exception.message)

    def test_spec_validate_fails_with_bad_id_ref(self):

        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(INVALID_SPEC_BAD_ID_REFERENCE)
            temp_spec.seek(0)

            with self.assertRaises(AacSpecValidationException) as context_manager:
                spec_validate(temp_spec.name)

                validation_exception = context_manager.exception
                self.assertIn("Invalid requirement id 3 reference in", validation_exception.message)

    def test_spec_validate_fails_with_bad_abbrv_ref(self):

        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(INVALID_SPEC_BAD_ID_REFERENCE)
            temp_spec.seek(0)

            with self.assertRaises(AacSpecValidationException) as context_manager:
                spec_validate(temp_spec.name)

                validation_exception = context_manager.exception
                self.assertIn("Invalid requirement abbreviation NOTSUB reference in", validation_exception.message)


VALID_SPEC = """
spec:
  name: Subsystem
  abbreviation: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
spec:
  name: Module
  abbreviation: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbreviation: SUB
          ids: 1
      attributes:
        - name: TADI
          value: Test
"""

INVALID_SPEC_MISSING_ABRV = """
spec:
  name: Subsystem
  abbreviation:
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
spec:
  name: Module
  abbreviation: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbreviation: SUB_SYS
          ids: 1
      attributes:
        - name: TADI
          value: Test
"""

INVALID_SPEC_BAD_ID_REFERENCE = """
spec:
  name: Subsystem
  abbreviation: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
spec:
  name: Module
  abbreviation: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbreviation: SUB
          ids: 3
      attributes:
        - name: TADI
          value: Test
"""

INVALID_SPEC_BAD_ABBRV_VALUE = """
spec:
  name: Subsystem
  abbreviation: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
spec:
  name: Module
  abbreviation: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbreviation: NOTSUB
          ids: 1
      attributes:
        - name: TADI
          value: Test
"""
