import re
from unittest import TestCase

from aac import util, validator
from aac.parser import parse_str
from aac.validator import is_valid, validate_and_get_errors


def kw(**kwargs):
    """Return a dictionary of the provided keyword arguments."""
    return kwargs


def o(model: str, **kwargs):
    """Return a simulated model after being parsed."""
    root = ("name" in kwargs and kwargs["name"]) or "root"
    return {root: {model: kwargs}}


def enum(**kwargs):
    """Return a simulated enum model."""
    return o("enum", **kwargs)


def data(**kwargs):
    """Return a simulated data model."""
    return o("data", **kwargs)


def usecase(**kwargs):
    """Return a simulated usecase model."""
    return o("usecase", **kwargs)


def model(**kwargs):
    """Return a simulated system model."""
    return o("model", **kwargs)


def ext(**kwargs):
    """Return a simulated ext model."""
    return o("ext", **kwargs)


def assert_errors_contain(self, errors, pattern):
    """Assert that at least one error in ERRORS matches PATTERN."""

    def assertion(e):
        return re.search(pattern, e) is not None

    self.failIf(not any(map(assertion, errors)), f"did not find '{pattern}' in {errors}")


def assert_model_is_valid(self, model):
    """Assert that the provided MODEL is valid."""
    self.assertEqual(validate_and_get_errors(model), [])


def assert_model_is_invalid(self, model, error_pattern):
    """Assert that the provided MODEL is invalid."""
    errors = validate_and_get_errors(model)
    self.assertNotEqual(errors, [])
    assert_errors_contain(self, errors, error_pattern)


class ValidatorTest(TestCase):
    MODEL_NAME = "test"

    ENUM_VALID_VALUES = ["a", "b"]

    DATA_VALID_FIELDS = [kw(name="x", type="int"), kw(name="y", type="int")]
    DATA_INVALID_FIELDS = [kw(name="x'", type="invalid"), kw(name="y'", type="invalid[]")]

    def setUp(self):
        util.AAC_MODEL = {}
        validator.VALID_TYPES = []

    def test_is_valid(self):
        self.assertTrue(is_valid(data(name="test", fields=[kw(name="a", type="int")])))
        self.assertFalse(is_valid(data()))

    def test_valid_enums_pass_validation(self):
        name = self.MODEL_NAME
        values = self.ENUM_VALID_VALUES
        enums = [enum(name=name, values=values[:i]) for i in range(len(values))]

        for e in enums:
            assert_model_is_valid(self, e)

    def test_enum_with_missing_values_fails_validation(self):
        pattern = "missing.*required.*(name|values)"
        assert_model_is_invalid(self, enum(), pattern)

    def test_enum_with_unrecognized_fields_fails_validation(self):
        pattern = "unrecognized.*field.*invalid"
        assert_model_is_invalid(self, enum(invalid="item"), pattern)

    def test_valid_data_pass_validation(self):
        name = self.MODEL_NAME
        fields = self.DATA_VALID_FIELDS

        data_none_required = [data(name=name, fields=fields[:i]) for i in range(len(fields))]
        data_with_required = [
            data(
                name=name,
                fields=fields[:i],
                required=[f["name"] for f in fields if fields.index(f) <= i - 1],
            )
            for i in range(len(fields))
        ]

        for d in data_none_required + data_with_required:
            assert_model_is_valid(self, d)

    def test_data_with_missing_fields_fails_validation(self):
        pattern = "missing.*required.*(name|fields)"
        assert_model_is_invalid(self, data(), pattern)

    def test_data_with_unrecognized_fields_fails_validation(self):
        pattern = "unrecognized.*field.*invalid"
        assert_model_is_invalid(self, data(invalid="item"), pattern)

    def test_data_with_unrecognized_type_fails_validation(self):
        name = self.MODEL_NAME
        fields = self.DATA_INVALID_FIELDS
        pattern = "unrecognized.*type.*invalid(\\[\\])?.*test"

        assert_model_is_invalid(self, data(name=name, fields=fields), pattern)

    def test_data_with_undefined_references_to_required_fields_fails_validation(self):
        name = self.MODEL_NAME
        fields = self.DATA_INVALID_FIELDS
        pattern = "reference.*undefined.*(x|z)"
        required = ["x", "z"]

        test_data = [
            data(name=name, fields=fields[:i], required=[required[i]]) for i in range(len(fields))
        ]

        for d in test_data:
            assert_model_is_invalid(self, d, pattern)

    def test_can_validate_usecase(self):
        one_part = [kw(name="x", type="X")]
        two_parts = one_part + [kw(name="y", type="Y")]

        one_step = [kw(step="alpha", source="x", target="y", action="b")]
        two_steps = one_step + [kw(step="beta", source="y", target="x", action="b")]

        assert_model_is_valid(self, usecase(name="test", participants=[], steps=[]))
        assert_model_is_valid(self, usecase(name="test", participants=one_part, steps=[]))
        assert_model_is_valid(self, usecase(name="test", participants=two_parts, steps=[]))
        assert_model_is_valid(self, usecase(name="test", participants=[], steps=one_step))
        assert_model_is_valid(self, usecase(name="test", participants=[], steps=two_steps))
        assert_model_is_valid(self, usecase(name="test", participants=one_part, steps=one_step))
        assert_model_is_valid(
            self,
            usecase(
                name="test", participants=one_part, steps=one_step, description="test description"
            ),
        )

        assert_model_is_invalid(self, usecase(), "missing.*required.*(name|participants|steps)")
        assert_model_is_invalid(self, usecase(invalid="item"), "unrecognized.*field.*invalid")

    def test_can_validate_models(self):
        # TODO: Figure out how to clear out the spec before running each test so we don't assume
        # behaviors must have descriptions
        one_behavior = [kw(name="test", type="pub-sub", acceptance=[], description="stuff")]
        two_behaviors = one_behavior + [
            kw(name="test", type="pub-sub", acceptance=[], description="more stuff")
        ]

        assert_model_is_valid(self, model(name="test", behavior=[]))
        assert_model_is_valid(self, model(name="test", behavior=one_behavior))
        assert_model_is_valid(self, model(name="test", behavior=two_behaviors))
        assert_model_is_valid(
            self, model(name="test", behavior=one_behavior, description="description")
        )
        assert_model_is_valid(self, model(name="test", behavior=one_behavior, components=[]))
        assert_model_is_valid(
            self,
            model(name="test", behavior=one_behavior, components=[kw(name="a", type="string")]),
        )
        assert_model_is_valid(
            self,
            model(name="test", behavior=one_behavior, description="description", components=[]),
        )
        assert_model_is_valid(
            self,
            model(
                name="test",
                behavior=one_behavior,
                description="description",
                components=[kw(name="a", type="string[]")],
            ),
        )

        assert_model_is_invalid(self, model(), "missing.*required.*(name|behavior)")
        assert_model_is_invalid(self, model(invalid="item"), "unrecognized.*field.*invalid")
        assert_model_is_invalid(
            self,
            model(name="test", behavior=[kw(name="test", type="Nothing", acceptance=[kw()])]),
            "missing.*required.*(scenario|when|then)",
        )
        assert_model_is_invalid(
            self,
            model(
                name="test",
                behavior=[kw(name="test", type="pub-sub", acceptance=[], input=[kw()])],
            ),
            "missing.*required.*(name|type)",
        )
        assert_model_is_invalid(
            self,
            model(
                name="test",
                behavior=[kw(name="test", type="pub-sub", acceptance=[], output=[kw()])],
            ),
            "missing.*required.*(name|type)",
        )
        assert_model_is_invalid(
            self,
            model(
                name="test",
                behavior=[kw(name="test", type="bad", acceptance=[], output=[kw()])],
            ),
            "unrecognized.*BehaviorType.*bad.*test",
        )

    def test_can_validate_extensions(self):
        assert_model_is_valid(self, ext(name="test", type="Primitives", enumExt=kw(add=[])))
        assert_model_is_valid(self, ext(name="test", type="Primitives", enumExt=kw(add=["a"])))
        assert_model_is_valid(
            self, ext(name="test", type="Primitives", enumExt=kw(add=["a", "b"]))
        )
        assert_model_is_valid(self, ext(name="test", type="model", dataExt=kw(add=[])))
        assert_model_is_valid(
            self, ext(name="test", type="model", dataExt=kw(add=[kw(name="a", type="int")]))
        )
        assert_model_is_valid(
            self,
            ext(
                name="test",
                type="model",
                dataExt=kw(add=[kw(name="a", type="int"), kw(name="b", type="int")]),
            ),
        )
        assert_model_is_valid(
            self,
            ext(
                name="CommandBehaviorInput",
                type="Behavior",
                dataExt=kw(add=[kw(name="description", type="string")], required=["description"]),
            ),
        )

        assert_model_is_invalid(
            self, ext(name="test", type="Primitives"), "unrecognized.*extension.*type"
        )
        assert_model_is_invalid(
            self,
            ext(name="test", type="invalid"),
            "unrecognized.*extension.*type.*invalid",
        )
        assert_model_is_invalid(self, ext(), "missing.*required.*(name|type)")
        assert_model_is_invalid(self, ext(invalid="item"), "unrecognized.*field.*invalid")
        assert_model_is_invalid(
            self,
            ext(name="", type="", enumExt=kw(), dataExt=kw()),
            "cannot.*combine.*enumExt.*dataExt",
        )
        assert_model_is_invalid(
            self,
            ext(name="", type="", dataExt=kw(add=[kw()])),
            "missing.*required.*field.*(name|type)",
        )
        assert_model_is_invalid(
            self,
            o("bad", name=""),
            "bad.*not.*AaC.*root",
        )


class ValidatorFunctionalTest(TestCase):
    def setUp(self):
        util.AAC_MODEL = {}
        validator.VALID_TYPES = []

    def test_full(self):
        model = parse_str(
            """
enum:
  name: us-time-zone
  values:
    - est
    - cst
    - mst
    - pst
---
data:
  name: time
  fields:
    - name: hours
      type: int
    - name: minutes
      type: int
    - name: seconds
      type: int
---
ext:
  name: zoned-time
  type: time
  dataExt:
    add:
      - name: tzone
        type: us-time-zone
---
model:
  name: clock
  behavior:
    - name: publish current time
      type: pub-sub
      input:
        - name: time-to-set
          type: zoned-time
      output:
        - name: current-time
          type: zoned-time
      acceptance:
        - scenario: publish current time
          when:
            - waiting 1 second
          then:
            - will publish current-time
            - will be completed within 5 milliseconds
        """,
            "validation-test",
        )
        assert_model_is_valid(self, model)

    def test_extension(self):
        model = parse_str(
            """
ext:
   name: CommandBehaviorType
   type: BehaviorType
   enumExt:
      add:
         - command
---
ext:
   name: CommandBehaviorInput
   type: Behavior
   dataExt:
      add:
        - name: description
          type: string
---
model:
  name: clock
  behavior:
    - name: say goodmorning
      type: command
      input:
        - name: name
          type: string
      output:
        - name: good-morning
          type: string
      acceptance:
        - scenario: time to wake up
          when:
            - waiting 1 second
          then:
            - will say good-morning
""",
            "validation-test",
        )
        assert_model_is_valid(self, model)
