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


class ValidatorTest(TestCase):
    def assert_errors_contain(self, errors, pattern):
        """Assert that at least one error in ERRORS matches PATTERN."""

        def assertion(e):
            return re.search(pattern, e) is not None

        self.failIf(not any(map(assertion, errors)), f"did not find '{pattern}' in {errors}")

    def assert_model_is_valid(self, model):
        """Assert that the provided MODEL is valid."""
        self.assertTrue(validator.is_valid(model))
        self.assertEquals(validator.get_all_errors(model), [])

    def assert_model_is_invalid(self, model, error_pattern):
        """Assert that the provided MODEL is invalid."""
        self.assertFalse(validator.is_valid(model))

        errors = validator.get_all_errors(model)
        self.assertNotEquals(errors, [])
        self.assert_errors_contain(errors, error_pattern)

    def test_can_validate_enums(self):
        self.assert_model_is_valid(enum(name="test", values=[]))
        self.assert_model_is_valid(enum(name="test", values=["a"]))
        self.assert_model_is_valid(enum(name="test", values=["a", "b"]))

        self.assert_model_is_invalid(enum(), "missing.*required.*(name|values)")
        self.assert_model_is_invalid(enum(name="test"), "missing.*required.*values")
        self.assert_model_is_invalid(enum(values=[]), "missing.*required.*name")
        self.assert_model_is_invalid(enum(invalid="item"), "unrecognized.*field.*invalid")

    def test_can_validate_data(self):
        one_field = [kw(name="x", type="int")]
        two_fields = one_field + [kw(name="y", type="int")]

        self.assert_model_is_valid(data(name="test", fields=[]))
        self.assert_model_is_valid(data(name="test", fields=one_field))
        self.assert_model_is_valid(data(name="test", fields=two_fields))

        self.assert_model_is_valid(data(name="test", fields=[], required=[]))
        self.assert_model_is_valid(data(name="test", fields=one_field, required=["x"]))
        self.assert_model_is_valid(data(name="test", fields=two_fields, required=["x"]))
        self.assert_model_is_valid(data(name="test", fields=two_fields, required=["x", "y"]))

        self.assert_model_is_invalid(data(), "missing.*required.*(name|fields)")
        self.assert_model_is_invalid(data(name="test"), "missing.*required.*fields")
        self.assert_model_is_invalid(data(fields=[]), "missing.*required.*name")
        self.assert_model_is_invalid(
            data(
                name="Message",
                fields=[
                    kw(name="to", type="EmailAddress"),
                    kw(name="from", type="EmailAddress[]"),
                ],
            ),
            "unrecognized.*type.*EmailAddress(\\[\\])?.*Message",
        )

        self.assert_model_is_invalid(data(invalid="item"), "unrecognized.*field.*invalid")

        self.assert_model_is_invalid(
            data(name="test", fields=[], required=["x"]), "reference.*undefined.*x"
        )
        self.assert_model_is_invalid(
            data(name="test", fields=two_fields, required=["z"]), "reference.*undefined.*z"
        )

    def test_can_validate_usecase(self):
        one_part = [kw(name="x", type="X")]
        two_parts = one_part + [kw(name="y", type="Y")]

        one_step = [kw(step="alpha", source="x", target="y", action="b")]
        two_steps = one_step + [kw(step="beta", source="y", target="x", action="b")]

        self.assert_model_is_valid(usecase(name="test", participants=[], steps=[]))
        self.assert_model_is_valid(usecase(name="test", participants=one_part, steps=[]))
        self.assert_model_is_valid(usecase(name="test", participants=two_parts, steps=[]))
        self.assert_model_is_valid(usecase(name="test", participants=[], steps=one_step))
        self.assert_model_is_valid(usecase(name="test", participants=[], steps=two_steps))
        self.assert_model_is_valid(usecase(name="test", participants=one_part, steps=one_step))
        self.assert_model_is_valid(
            usecase(
                name="test", participants=one_part, steps=one_step, description="test description"
            )
        )

        self.assert_model_is_invalid(usecase(), "missing.*required.*(name|participants|steps)")
        self.assert_model_is_invalid(usecase(invalid="item"), "unrecognized.*field.*invalid")

    def test_can_validate_models(self):
        one_behavior = [kw(name="test", type="pub-sub", acceptance=[])]
        two_behaviors = one_behavior + [kw(name="test", type="pub-sub", acceptance=[])]

        self.assert_model_is_valid(model(name="test", behavior=[]))
        self.assert_model_is_valid(model(name="test", behavior=one_behavior))
        self.assert_model_is_valid(model(name="test", behavior=two_behaviors))
        self.assert_model_is_valid(
            model(name="test", behavior=one_behavior, description="description")
        )
        self.assert_model_is_valid(model(name="test", behavior=one_behavior, components=[]))
        self.assert_model_is_valid(
            model(name="test", behavior=one_behavior, components=[kw(name="a", type="string")])
        )
        self.assert_model_is_valid(
            model(name="test", behavior=one_behavior, description="description", components=[])
        )
        self.assert_model_is_valid(
            model(
                name="test",
                behavior=one_behavior,
                description="description",
                components=[kw(name="a", type="string[]")],
            )
        )

        self.assert_model_is_invalid(model(), "missing.*required.*(name|behavior)")
        self.assert_model_is_invalid(model(invalid="item"), "unrecognized.*field.*invalid")
        self.assert_model_is_invalid(
            model(name="test", behavior=[kw(name="test", type="Nothing", acceptance=[kw()])]),
            "missing.*required.*(scenario|when|then)",
        )
        self.assert_model_is_invalid(
            model(
                name="test",
                behavior=[kw(name="test", type="pub-sub", acceptance=[], input=[kw()])],
            ),
            "missing.*required.*(name|type)",
        )
        self.assert_model_is_invalid(
            model(
                name="test",
                behavior=[kw(name="test", type="pub-sub", acceptance=[], output=[kw()])],
            ),
            "missing.*required.*(name|type)",
        )
        self.assert_model_is_invalid(
            model(
                name="test",
                behavior=[kw(name="test", type="bad", acceptance=[], output=[kw()])],
            ),
            "entry.*value.*bad.*not.*allowed",
        )

    def test_can_validate_extensions(self):
        self.assert_model_is_valid(ext(name="test", type="int"))
        self.assert_model_is_valid(ext(name="test", type="int", enumExt=kw(add=[])))
        self.assert_model_is_valid(ext(name="test", type="int", enumExt=kw(add=["a"])))
        self.assert_model_is_valid(ext(name="test", type="int", enumExt=kw(add=["a", "b"])))
        self.assert_model_is_valid(ext(name="test", type="int", dataExt=kw(add=[])))
        self.assert_model_is_valid(
            ext(name="test", type="int", dataExt=kw(add=[kw(name="a", type="int")]))
        )
        self.assert_model_is_valid(
            ext(
                name="test",
                type="int",
                dataExt=kw(add=[kw(name="a", type="int"), kw(name="b", type="int")]),
            )
        )

        self.assert_model_is_invalid(ext(), "missing.*required.*(name|type)")
        self.assert_model_is_invalid(ext(invalid="item"), "unrecognized.*field.*invalid")
        self.assert_model_is_invalid(
            ext(name="", type="", enumExt=kw(), dataExt=kw()), "cannot.*combine.*enumExt.*dataExt"
        )
        self.assert_model_is_invalid(
            ext(name="", type="", dataExt=kw(add=[kw()])), "missing.*required.*field.*(name|type)"
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
        self.assert_model_is_valid(models)

        self.assert_model_is_invalid(o("invalid", name="test"), "invalid.*not.*recognized.*root")

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
