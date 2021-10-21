import re
from enum import Enum
from unittest import TestCase

from aac import validator


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
    self.assertEquals(validator.get_all_errors(model), [])


def assert_model_is_invalid(self, model, error_pattern):
    """Assert that the provided MODEL is invalid."""
    errors = validator.get_all_errors(model)
    self.assertNotEquals(errors, [])
    assert_errors_contain(self, errors, error_pattern)


class ValidatorTest(TestCase):
    def test_is_valid(self):
        self.assertTrue(validator.is_valid(data(name="test", fields=[kw(name="a", type="int")])))
        self.assertFalse(validator.is_valid(data()))

    def test_can_validate_enums(self):
        assert_model_is_valid(self, enum(name="test", values=[]))
        assert_model_is_valid(self, enum(name="test", values=["a"]))
        assert_model_is_valid(self, enum(name="test", values=["a", "b"]))

        assert_model_is_invalid(self, enum(), "missing.*required.*(name|values)")
        assert_model_is_invalid(self, enum(name="test"), "missing.*required.*values")
        assert_model_is_invalid(self, enum(values=[]), "missing.*required.*name")
        assert_model_is_invalid(self, enum(invalid="item"), "unrecognized.*field.*invalid")

    def test_can_validate_data(self):
        one_field = [kw(name="x", type="int")]
        two_fields = one_field + [kw(name="y", type="int")]

        assert_model_is_valid(self, data(name="test", fields=[]))
        assert_model_is_valid(self, data(name="test", fields=one_field))
        assert_model_is_valid(self, data(name="test", fields=two_fields))

        assert_model_is_valid(self, data(name="test", fields=[], required=[]))
        assert_model_is_valid(self, data(name="test", fields=one_field, required=["x"]))
        assert_model_is_valid(self, data(name="test", fields=two_fields, required=["x"]))
        assert_model_is_valid(self, data(name="test", fields=two_fields, required=["x", "y"]))

        assert_model_is_invalid(self, data(), "missing.*required.*(name|fields)")
        assert_model_is_invalid(self, data(name="test"), "missing.*required.*fields")
        assert_model_is_invalid(self, data(fields=[]), "missing.*required.*name")
        assert_model_is_invalid(
            self,
            data(
                name="Message",
                fields=[
                    kw(name="to", type="EmailAddress"),
                    kw(name="from", type="EmailAddress[]"),
                ],
            ),
            "unrecognized.*type.*EmailAddress(\\[\\])?.*Message",
        )

        assert_model_is_invalid(self, data(invalid="item"), "unrecognized.*field.*invalid")

        assert_model_is_invalid(
            self, data(name="test", fields=[], required=["x"]), "reference.*undefined.*x"
        )
        assert_model_is_invalid(
            self, data(name="test", fields=two_fields, required=["z"]), "reference.*undefined.*z"
        )

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
        one_behavior = [kw(name="test", type="pub-sub", acceptance=[])]
        two_behaviors = one_behavior + [kw(name="test", type="pub-sub", acceptance=[])]

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
            "entry.*value.*bad.*not.*allowed",
        )

    def test_can_validate_extensions(self):
        assert_model_is_valid(self, ext(name="test", type="int"))
        assert_model_is_valid(self, ext(name="test", type="int", enumExt=kw(add=[])))
        assert_model_is_valid(self, ext(name="test", type="int", enumExt=kw(add=["a"])))
        assert_model_is_valid(self, ext(name="test", type="int", enumExt=kw(add=["a", "b"])))
        assert_model_is_valid(self, ext(name="test", type="int", dataExt=kw(add=[])))
        assert_model_is_valid(
            self, ext(name="test", type="int", dataExt=kw(add=[kw(name="a", type="int")]))
        )
        assert_model_is_valid(
            self,
            ext(
                name="test",
                type="int",
                dataExt=kw(add=[kw(name="a", type="int"), kw(name="b", type="int")]),
            ),
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

    def test_can_detect_cross_referencing_errors(self):
        models = [
            data(name="TestData1", fields=[kw(name="one", type="string")]),
            data(name="TestData2", fields=[kw(name="two", type="string")]),
            data(
                name="TestData3",
                fields=[kw(name="a", type="TestData1"), kw(name="b", type="TestData2")],
            ),
        ]
        # assert_model_is_valid(self, models)

        assert_model_is_invalid(self, o("invalid", name="test"), "invalid.*not.*recognized.*root")

    def test_can_load_aac_data(self):
        enum_items = [
            {"name": "name", "type": "string", "required": True},
            {"name": "values", "type": "string[]", "required": True},
        ]

        data_items = [
            {"name": "name", "type": "string", "required": True},
            {"name": "fields", "type": "Field[]", "required": True},
            {"name": "required", "type": "string[]", "required": False},
        ]

        extension_items = [
            {"name": "name", "type": "string", "required": True},
            {"name": "type", "type": "string", "required": True},
            {"name": "enumExt", "type": "EnumExtension", "required": False},
            {"name": "dataExt", "type": "DataExtension", "required": False},
        ]

        self.assertListEqual(validator.load_aac_fields_for("enum"), enum_items)
        self.assertListEqual(validator.load_aac_fields_for("data"), data_items)
        self.assertListEqual(validator.load_aac_fields_for("extension"), extension_items)


class ValidatorFunctionalTest(TestCase):
    def test_full(self):
        from aac import parser

        model = parser.parse_str(
            """
enum:
  name: time-zone
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
        type: time-zone
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
