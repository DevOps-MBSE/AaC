from unittest import TestCase
from tempfile import NamedTemporaryFile

from aac_spec.aac_spec_impl import _do_validate, spec_validate, AacSpecValidationException


class TestAacSpec(TestCase):

    def test_spec_validate(self):

        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(VALID_SPEC)

            try:
                spec_validate(temp_spec.name)
            except AacSpecValidationException as e:
                self.fail("validate() raised AacSpecValidationException with error: {0}".format(e))

    def test_spec_validate_fails(self):

        with NamedTemporaryFile("w") as temp_spec:
            temp_spec.write(INVALID_SPEC_1)

            with self.assertRaises(AacSpecValidationException) as context_manager:
                spec_validate(temp_spec.name)


VALID_SPEC = """
spec:
  name: Subsystem
  abbrv: SUB
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
  abbrv: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbrv: SUB
          ids: 1
      attributes:
        - name: TADI
          value: Test
"""

INVALID_SPEC_1 = """
spec:
  name: Subsystem
  abbrv: SUB
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
  abbrv: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbrv: SUB_SYS
          ids: 1
      attributes:
        - name: TADI
          value: Test
"""

INVALID_SPEC_2 = """
spec:
  name: Subsystem
  abbrv: SUB
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
  abbrv: MOD
  description:  This is a representative module requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the module shall respond with a value.
      parent:
        - abbrv: SUB
          ids: 3
      attributes:
        - name: TADI
          value: Test
"""

VALID_MODEL = """
spec:
  name: Subsystem
  abbrv: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
model:
  name: Test
  description: This is a test model.
  behavior:
    - name: do_stuff
      type: pub-sub
      requirements:
        - abbrv: SUB
          ids: 1
"""

INVALID_MODEL_1 = """
spec:
  name: Subsystem
  abbrv: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
model:
  name: Test
  description: This is a test model.
  behavior:
    - name: do_stuff
      type: pub-sub
      requirements:
        - abbrv: SUB_SYS
          ids: 1
"""

INVALID_MODEL_2 = """
spec:
  name: Subsystem
  abbrv: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
model:
  name: Test
  description: This is a test model.
  behavior:
    - name: do_stuff
      type: pub-sub
      requirements:
        - abbrv: SUB
          ids: 9
"""

VALID_DATA = """
spec:
  name: Subsystem
  abbrv: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
data:
  name: Message
  requirements:
    - abbrv: SUB
      ids: 1
  fields:
    - name: header
      type: string
    - name: body
      type: string
  required:
    - header
"""

INVALID_DATA_1 = """
spec:
  name: Subsystem
  abbrv: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
data:
  name: Message
  requirements:
    - abbrv: SUB_SYS
      ids: 1
  fields:
    - name: header
      type: string
    - name: body
      type: string
  required:
    - header
"""

INVALID_DATA_2 = """
spec:
  name: Subsystem
  abbrv: SUB
  description:  This is a representative subsystem requirement specification.
  requirements:
    - id: 1
      shall:  When receiving a message, the subsystem shall respond with a value.
      attributes:
        - name: TADI
          value: Test
---
data:
  name: Message
  requirements:
    - abbrv: SUB
      ids: 10
  fields:
    - name: header
      type: string
    - name: body
      type: string
  required:
    - header
"""
