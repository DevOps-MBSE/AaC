import re
from unittest import TestCase

from aac import util, validator

assert_status_is_false = lambda status: assert_status_is(status, False)
assert_status_is_true = lambda status: assert_status_is(status, True)


def assert_status_is(status, expected_status):
    assert status is expected_status


def assert_errors_exist(errors):
    assert len(errors) > 0


def assert_errors_contain(errors, pattern):
    for e in errors:
        assert re.search(pattern, e)


class ValidatorTest(TestCase):
    def test_validation_fails_when_model_has_unrecognized_fields(self):
        status, errors = validator.validate_model_entry(
            "data",
            "data",
            {"name": "test", "fields": {}, "unrecognized": "key"},
            *util.getAaCSpec(),
        )

        assert_status_is_false(status)
        assert_errors_exist(errors)
        assert_errors_contain(errors, "unrecognized.*field.*unrecognized")

    def test_validation_fails_when_model_has_more_than_one_root_item(self):
        status, errors = validator.validate_general({"a": 1, "b": 2})

        assert_status_is_false(status)
        assert_errors_exist(errors)
        assert_errors_contain(errors, "more.*one.*root")

    def test_validation_fails_when_model_has_unknown_root(self):
        status, errors = validator.validate_general({"a": 1})

        assert_status_is_false(status)
        assert_errors_exist(errors)
        assert_errors_contain(errors, "unrecognized.*root.*[a]")
