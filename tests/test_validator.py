import re
from enum import Enum
from unittest import TestCase

from aac import validator


def assert_status_is_false(status):
    """Assert STATUS is False."""
    assert_status_is(status, False)


def assert_status_is_true(status):
    """Assert STATUS is True."""
    assert_status_is(status, True)


def assert_status_is(status, expected_status):
    """Assert STATUS is EXPECTED_STATUS."""
    assert status is expected_status


def assert_errors_exist(errors):
    """Assert that ERRORS is a non-empty collection."""
    assert len(errors) > 0


def assert_no_errors(errors):
    """Assert that ERRORS is an empty collection."""
    assert len(errors) == 0


def assert_errors_contain(errors, pattern):
    """Assert that at least one error in ERRORS matches PATTERN."""

    def assertion(e):
        return re.search(pattern, e)

    assert filter(lambda x: x is not None, map(assertion, errors))


def assert_model_is_valid(model):
    """Assert that the provided MODEL is valid."""
    assert_status_is_true(validator.is_valid(model))
    assert_no_errors(validator.get_all_errors(model))


def assert_model_is_invalid(model, error_pattern):
    """Assert that the provided MODEL is invalid."""
    assert_status_is_false(validator.is_valid(model))

    errors = validator.get_all_errors(model)
    assert_errors_exist(errors)
    assert_errors_contain(errors, error_pattern)


def kw(**kwargs):
    """Return a dictionary of the provided keyword arguments."""
    return kwargs


def o(model: str, **kwargs):
    """Return a simulated model after being parsed."""
    root = ("name" in kwargs and kwargs["name"]) or "root"
    return {root: {model: kwargs}}


class ValidatorTest(TestCase):
    def test_can_validate_enums(self):
        def enum(**kwargs):
            return o("enum", **kwargs)

        assert_model_is_valid(enum(name="test", values=[]))
        assert_model_is_valid(enum(name="test", values=["a"]))
        assert_model_is_valid(enum(name="test", values=["a", "b"]))

        assert_model_is_invalid(enum(), "missing.*required.*(name|values)")
        assert_model_is_invalid(enum(name="test"), "missing.*required.*values")
        assert_model_is_invalid(enum(values=[]), "missing.*required.*name")
        assert_model_is_invalid(enum(name=1, values=2), "wrong.*type.*(name|values)")
        assert_model_is_invalid(enum(invalid="item"), "unrecognized.*property.*invalid")

    def test_can_validate_data(self):
        def data(**kwargs):
            return o("data", **kwargs)

        one_field = [kw(name="x", type="int")]
        two_fields = one_field + [kw(name="y", type="int")]

        assert_model_is_valid(data(name="test", fields=[]))
        assert_model_is_valid(data(name="test", fields=one_field))
        assert_model_is_valid(data(name="test", fields=two_fields))

        assert_model_is_valid(data(name="test", fields=[], required=[]))
        assert_model_is_valid(data(name="test", fields=one_field, required=["x"]))
        assert_model_is_valid(data(name="test", fields=two_fields, required=["x"]))
        assert_model_is_valid(data(name="test", fields=two_fields, required=["x", "y"]))

        assert_model_is_invalid(data(), "missing.*required.*(name|fields)")
        assert_model_is_invalid(data(name="test"), "missing.*required.*fields")
        assert_model_is_invalid(data(fields=[]), "missing.*required.*name")
        assert_model_is_invalid(data(invalid="item"), "unrecognized.*property.*invalid")

        assert_model_is_invalid(data(name=1, fields=2), "wrong.*type.*(name|fields)")
        assert_model_is_invalid(
            data(name=1, fields=2, required=3), "wrong.*type.*(name|fields|required)"
        )
        assert_model_is_invalid(
            data(name="test", fields=[kw(name=1, type=2)]), "wrong.*type.*field.*(name|type)"
        )

        assert_model_is_invalid(
            data(name="test", fields=[], required=["x"]), "reference.*undefined.*x"
        )
        assert_model_is_invalid(
            data(name="test", fields=two_fields, required=["z"]), "reference.*undefined.*z"
        )

    def test_can_validate_usecase(self):
        def usecase(**kwargs):
            return o("usecase", **kwargs)

        one_part = [kw(name="x", type="X")]
        two_parts = one_part + [kw(name="y", type="Y")]

        one_step = [kw(step="alpha", source="x", target="y", action="b")]
        two_steps = one_step + [kw(step="beta", source="y", target="x", action="b")]

        assert_model_is_valid(usecase(name="test", participants=[], steps=[]))
        assert_model_is_valid(usecase(name="test", participants=one_part, steps=[]))
        assert_model_is_valid(usecase(name="test", participants=two_parts, steps=[]))
        assert_model_is_valid(usecase(name="test", participants=[], steps=one_step))
        assert_model_is_valid(usecase(name="test", participants=[], steps=two_steps))
        assert_model_is_valid(usecase(name="test", participants=one_part, steps=one_step))
        assert_model_is_valid(
            usecase(
                name="test", participants=one_part, steps=one_step, description="test description"
            )
        )

        assert_model_is_invalid(usecase(), "missing.*required.*(name|participants|steps)")
        assert_model_is_invalid(usecase(invalid="item"), "unrecognized.*property.*invalid")
        assert_model_is_invalid(
            usecase(name=1, participants=2, steps=3), "wrong.*type.*(name|participants|steps)"
        )
        assert_model_is_invalid(
            usecase(name=1, participants=2, steps=3, description=4),
            "wrong.*type.*(name|participants|steps|description)",
        )

        assert_model_is_invalid(
            usecase(name="test", participants=[kw(name=1, type=2)], steps=[]),
            "wrong.*type.*field.*(name|type)",
        )
        assert_model_is_invalid(
            usecase(
                name="test",
                participants=[],
                steps=[
                    kw(
                        **{
                            "step": 1,
                            "source": 2,
                            "target": 3,
                            "action": 4,
                            "if": 5,
                            "else": 6,
                            "loop": 7,
                        }
                    )
                ],
            ),
            "wrong.*type.*field.*(step|source|target|action|if|else|loop)",
        )

    def test_can_validate_models(self):
        def model(**kwargs):
            return o("model", **kwargs)

        class TestEnum(Enum):
            ONE = 1
            TWO = 2

        one_behavior = [kw(name="test", type=TestEnum.ONE, acceptance=[])]
        two_behaviors = one_behavior + [kw(name="test", type=TestEnum.TWO, acceptance=[])]

        assert_model_is_valid(model(name="test", behavior=[]))
        assert_model_is_valid(model(name="test", behavior=one_behavior))
        assert_model_is_valid(model(name="test", behavior=two_behaviors))
        assert_model_is_valid(model(name="test", behavior=one_behavior, description="description"))
        assert_model_is_valid(model(name="test", behavior=one_behavior, components=[]))
        assert_model_is_valid(
            model(name="test", behavior=one_behavior, components=[kw(name="a", type="b")])
        )
        assert_model_is_valid(
            model(name="test", behavior=one_behavior, description="description", components=[])
        )
        assert_model_is_valid(
            model(
                name="test",
                behavior=one_behavior,
                description="description",
                components=[kw(name="a", type="b")],
            )
        )

        assert_model_is_invalid(model(), "missing.*required.*(name|behavior)")
        assert_model_is_invalid(model(invalid="item"), "unrecognized.*property.*invalid")
        assert_model_is_invalid(
            model(name=1, behavior=2, components=3, description=4),
            "wrong.*type.*(name|behavior|components|description)",
        )
        assert_model_is_invalid(
            model(name="test", behavior=[kw(name=1, type=2, acceptance=3)]),
            "wrong.*type.*field.*(name|type|acceptance)",
        )
        assert_model_is_invalid(
            model(name="test", behavior=[], components=[kw(name=1, type=2)]),
            "wrong.*type.*field.*(name|type)",
        )
        assert_model_is_invalid(
            model(name="test", behavior=[kw(name="test", type=TestEnum.ONE, acceptance=[kw()])]),
            "missing.*required.*(scenario|when|then)",
        )
        assert_model_is_invalid(
            model(
                name="test",
                behavior=[
                    kw(
                        name="test",
                        type=TestEnum.ONE,
                        acceptance=[kw(scenario=1, tags=2, given=3, when=4, then=5)],
                    )
                ],
            ),
            "wrong.*type.*field.*(scenario|tags|given|when|then)",
        )
        assert_model_is_invalid(
            model(
                name="test",
                behavior=[kw(name="test", type=TestEnum.ONE, acceptance=[], input=[kw()])],
            ),
            "missing.*required.*(name|type)",
        )
        assert_model_is_invalid(
            model(
                name="test",
                behavior=[
                    kw(name="test", type=TestEnum.ONE, acceptance=[], input=[kw(name=1, type=2)])
                ],
            ),
            "wrong.*type.*field.*(name|type)",
        )
        assert_model_is_invalid(
            model(
                name="test",
                behavior=[kw(name="test", type=TestEnum.ONE, acceptance=[], output=[kw()])],
            ),
            "missing.*required.*(name|type)",
        )
        assert_model_is_invalid(
            model(
                name="test",
                behavior=[
                    kw(name="test", type=TestEnum.ONE, acceptance=[], output=[kw(name=1, type=2)])
                ],
            ),
            "wrong.*type.*field.*(name|type)",
        )

    def test_can_validate_extensions(self):
        def ext(**kwargs):
            return o("ext", **kwargs)

        assert_model_is_valid(ext(name="test", type="int"))
        assert_model_is_valid(ext(name="test", type="int", enumExt=kw(add=[])))
        assert_model_is_valid(ext(name="test", type="int", enumExt=kw(add=["a"])))
        assert_model_is_valid(ext(name="test", type="int", enumExt=kw(add=["a", "b"])))
        assert_model_is_valid(ext(name="test", type="int", dataExt=kw(add=[])))
        assert_model_is_valid(
            ext(name="test", type="int", dataExt=kw(add=[kw(name="a", type="int")]))
        )
        assert_model_is_valid(
            ext(
                name="test",
                type="int",
                dataExt=kw(add=[kw(name="a", type="int"), kw(name="b", type="int")]),
            )
        )

        assert_model_is_invalid(ext(), "missing.*required.*(name|type)")
        assert_model_is_invalid(ext(invalid="item"), "unrecognized.*property.*invalid")
        assert_model_is_invalid(
            ext(name=1, type=2, enumExt=3, dataExt=4), "wrong.*type.*(name|type|enumExt|dataExt)"
        )
        assert_model_is_invalid(ext(name=1, type=2, enumExt=kw(add=1)), "wrong.*type.*field.*add")
        assert_model_is_invalid(ext(name=1, type=2, dataExt=kw(add=1)), "wrong.*type.*field.*add")
        assert_model_is_invalid(
            ext(name="", type="", enumExt=kw(), dataExt=kw()), "cannot.*combine.*enumExt.*dataExt"
        )
        assert_model_is_invalid(
            ext(name="", type="", dataExt=kw(add=[kw()])), "missing.*required.*field.*(name|type)"
        )
        assert_model_is_invalid(
            ext(name="", type="", dataExt=kw(add=[kw(name=1, type=2)])),
            "wrong.*type.*field.*(name|type)",
        )
