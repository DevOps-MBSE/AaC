from unittest import TestCase

from aac_spec_impl import _do_validate


class TestAacSpec(TestCase):

    def test_can_validate_spec(self):
        # TODO: test spec validation with correct spec definition
        # create a temp file with valid spec

        # do the validation and ensure is_valid and no errors
        is_valid, errors = _do_validate()
        self.assertTrue(False)

        # clean up

    def test_validate_spec_fails_for_bad_input(self):
        # TODO: test spec validation with invalid spec definition
        self.assertTrue(False)

    def test_can_validate_model_with_spec_refs(self):
        # TODO: test model validation with correct spec refs
        self.assertTrue(False)

    def test_validate_model_with_bad_spec_refs(self):
        # TODO: test model validation with incorrect spec refs
        self.assertTrue(False)

    def test_can_validate_data_with_spec_refs(self):
        # TODO: test model validation with correct spec refs
        self.assertTrue(False)

    def test_validate_data_with_bad_spec_refs(self):
        # TODO: test model validation with incorrect spec refs
        self.assertTrue(False)

    def _create_temp_test_file(content: str) -> str:
        return ""

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
