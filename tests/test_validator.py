import re
from unittest import TestCase

from aac import util, validator

assert_status_is_false = lambda status: assert_status_is(status, False)
assert_status_is_true = lambda status: assert_status_is(status, True)


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
    for e in errors:
        assert re.search(pattern, e)


def assert_model_is_valid(model):
    "Assert that the provided MODEL is valid."
    assert_status_is_true(validator.is_valid(model))
    assert_no_errors(validator.get_all_errors(model))


def assert_model_is_invalid(model, error_pattern):
    "Assert that the provided MODEL is valid."
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
        assert_model_is_valid(o("enum", name="test", values=[]))
        assert_model_is_valid(o("enum", name="test", values=["a"]))
        assert_model_is_valid(o("enum", name="test", values=["a", "b"]))

        assert_model_is_invalid(o("enum"), "missing.*required.*(name|values)")
        assert_model_is_invalid(o("enum", name="test"), "missing.*required.*values")
        assert_model_is_invalid(o("enum", values=[]), "missing.*required.*name")
        assert_model_is_invalid(o("enum", name=1, values=2), "wrong.*type.*(name|values)")

    def test_can_validate_data(self):
        one_field = [kw(name="x", type="int")]
        two_fields = one_field + [kw(name="y", type="int")]

        assert_model_is_valid(o("data", name="test", fields=[]))
        assert_model_is_valid(o("data", name="test", fields=one_field))
        assert_model_is_valid(o("data", name="test", fields=two_fields))

        assert_model_is_valid(o("data", name="test", fields=[], required=[]))
        assert_model_is_valid(o("data", name="test", fields=one_field, required=["x"]))
        assert_model_is_valid(o("data", name="test", fields=two_fields, required=["x"]))
        assert_model_is_valid(o("data", name="test", fields=two_fields, required=["x", "y"]))

        assert_model_is_invalid(o("data"), "missing.*required.*(name|fields)")
        assert_model_is_invalid(o("data", name="test"), "missing.*required.*fields")
        assert_model_is_invalid(o("data", fields=[]), "missing.*required.*name")

        assert_model_is_invalid(o("data", name=1, fields=2), "wrong.*type.*(name|fields)")
        assert_model_is_invalid(
            o("data", name=1, fields=2, required=3), "wrong.*type.*(name|fields|required)"
        )
        assert_model_is_invalid(
            o("data", name="test", fields=[kw(name=1, type=2)]), "wrong.*type.*field.*(name|type)"
        )

        assert_model_is_invalid(
            o("data", name="test", fields=[], required=["x"]), "reference.*undefined.*x"
        )
        assert_model_is_invalid(
            o("data", name="test", fields=two_fields, required=["z"]), "reference.*undefined.*z"
        )
