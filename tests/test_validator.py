import re
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
