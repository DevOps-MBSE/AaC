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

    VALID_FIELDS = [kw(name="x", type="int"), kw(name="y", type="int")]
    DATA_INVALID_FIELDS = [kw(name="x'", type="invalid"), kw(name="y'", type="invalid[]")]

    USECASE_STEPS = [
        kw(step="alpha", source="x", target="y", action="b"),
        kw(step="beta", source="y", target="x", action="b"),
    ]

    MODEL_ACCEPTANCE = [
        kw(scenario="scenario", given="given", when="when", then="then", tags=["tags"]),
        kw(scenario="scenario", when="when", then="then"),
    ]
    MODEL_BEHAVIORS = [
        kw(name="alpha", type="pub-sub", acceptance=MODEL_ACCEPTANCE, description="alpha"),
        kw(name="beta", type="pub-sub", acceptance=[], description="beta"),
        kw(name="gamma", type="pub-sub", acceptance=MODEL_ACCEPTANCE),
    ]

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
        fields = self.VALID_FIELDS

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

    def test_valid_usecases_with_only_participants_pass_validation(self):
        name = self.MODEL_NAME
        fields = self.VALID_FIELDS

        usecases = [
            usecase(name=name, participants=fields[:i], steps=[]) for i in range(len(fields))
        ]

        for u in usecases:
            assert_model_is_valid(self, u)

    def test_valid_usecases_with_only_steps_pass_validation(self):
        name = self.MODEL_NAME
        steps = self.USECASE_STEPS

        usecases = [
            usecase(name=name, participants=[], steps=steps[:i]) for i in range(len(steps))
        ]

        for u in usecases:
            assert_model_is_valid(self, u)

    def test_valid_usecases_with_participants_and_steps_pass_validation(self):
        name = self.MODEL_NAME
        fields = self.VALID_FIELDS
        steps = self.USECASE_STEPS

        usecases = [
            usecase(name=name, participants=fields[:i], steps=steps[:i]) for i in range(len(steps))
        ]

        for u in usecases:
            assert_model_is_valid(self, u)

    def test_valid_usecase_with_optional_description_passes_validation(self):
        name = self.MODEL_NAME
        fields = self.VALID_FIELDS
        steps = self.USECASE_STEPS
        desc = "A description"

        usecases = [
            usecase(name=name, participants=fields[:i], steps=steps[:i], description=desc)
            for i in range(len(steps))
        ]

        for u in usecases:
            assert_model_is_valid(self, u)

    def test_usecase_with_missing_fields_fails_validation(self):
        pattern = "missing.*required.*(name|participants|steps)"
        assert_model_is_invalid(self, usecase(), pattern)

    def test_usecase_with_unrecognized_fields_fails_validation(self):
        pattern = "unrecognized.*field.*invalid"
        assert_model_is_invalid(self, usecase(invalid="item"), pattern)

    def test_valid_models_with_only_required_fields_pass_validation(self):
        name = self.MODEL_NAME
        behaviors = self.MODEL_BEHAVIORS

        models = [model(name=name, behavior=behaviors[:i]) for i in range(len(behaviors))]

        for m in models:
            assert_model_is_valid(self, m)

    def test_valid_models_with_components_pass_validation(self):
        name = self.MODEL_NAME
        behaviors = self.MODEL_BEHAVIORS
        components = self.VALID_FIELDS

        models = [
            model(name=name, behavior=behaviors[:i], components=components)
            for i in range(len(behaviors))
        ]

        for m in models:
            assert_model_is_valid(self, m)

    def test_valid_models_with_components_and_description_pass_validation(self):
        name = self.MODEL_NAME
        behaviors = self.MODEL_BEHAVIORS
        components = self.VALID_FIELDS
        desc = "A description"

        models = [
            model(name=name, behavior=behaviors[:i], components=components[:i], description=desc)
            for i in range(len(behaviors))
        ]

        for m in models:
            assert_model_is_valid(self, m)

    def test_model_with_missing_fields_fails_validation(self):
        name = self.MODEL_NAME
        invalid_acceptance = kw(name=name, type="Nothing", acceptance=[kw()])
        invalid_input = kw(name=name, type="pub-sub", acceptance=[], input=[kw()])
        invalid_output = kw(name=name, type="pub-sub", acceptance=[], output=[kw()])

        models = [
            (model(), "name|behavior"),
            (model(name=name, behavior=[invalid_acceptance]), "scenario|when|then"),
            (model(name="test", behavior=[invalid_input]), "name|type"),
            (model(name="test", behavior=[invalid_output]), "name|type"),
        ]

        for m, names in models:
            assert_model_is_invalid(self, m, f"missing.*required.*({names})")

    def test_model_with_unrecognized_fields_fails_validation(self):
        pattern = "unrecognized.*field.*invalid"
        assert_model_is_invalid(self, model(invalid="item"), pattern)

    def test_model_with_unrecognized_behavior_type_fails_validation(self):
        name = self.MODEL_NAME
        invalid_behavior = kw(name="test", type="bad", acceptance=[], output=[kw()])
        pattern = "unrecognized.*BehaviorType.*bad.*test"
        assert_model_is_invalid(self, model(name=name, behavior=[invalid_behavior]), pattern)

    def test_valid_enum_extensions_pass_validation(self):
        name = self.MODEL_NAME
        added_fields = ["a", "b"]
        extensions = [
            ext(name=name, type="Primitives", enumExt=kw(add=added_fields[:i]))
            for i in range(len(added_fields))
        ]

        for e in extensions:
            assert_model_is_valid(self, e)

    def test_valid_data_extensions_pass_validation(self):
        name = self.MODEL_NAME
        added_fields = [kw(name="a", type="int"), kw(name="b", type="int")]
        extensions = [
            ext(name=name, type="model", dataExt=kw(add=added_fields[:i]))
            for i in range(len(added_fields))
        ]

        for e in extensions:
            assert_model_is_valid(self, e)

    def test_valid_data_extension_that_add_required_fields_pass_validation(self):
        name = self.MODEL_NAME
        data_extension = kw(add=[kw(name="new", type="string")], required=["new"])
        assert_model_is_valid(self, ext(name=name, type="Behavior", dataExt=data_extension))

    def test_extension_with_missing_fields_fails_validation(self):
        pattern = "missing.*required.*field.*(name|type)"
        assert_model_is_invalid(self, ext(name="", type="", dataExt=kw(add=[kw()])), pattern)

    def test_extension_with_unrecognized_behavior_type_fails_validation(self):
        name = self.MODEL_NAME
        pattern = "unrecognized.*extension.*type.*(invalid)?"

        for t in ["Primitives", "invalid"]:
            assert_model_is_invalid(self, ext(name=name, type=t), pattern)

    def test_extension_that_defines_enum_and_data_extensions_fails_validation(self):
        pattern = "cannot.*combine.*enumExt.*dataExt"
        assert_model_is_invalid(self, ext(name="", type="", enumExt=kw(), dataExt=kw()), pattern)

    def test_validation_fails_for_invalid_root_type(self):
        pattern = "bad.*not.*AaC.*root"
        assert_model_is_invalid(self, o("bad", name=""), pattern)


class ValidatorFunctionalTest(TestCase):

    def test_validates_parsed_yaml_models(self):
        model = parse_str(TEST_MODEL_WITH_EXTENSIONS, "validation-test")
        assert_model_is_valid(self, model)

    def test_validates_parsed_yaml_models_that_leverage_gen_pugin_extensions(self):
        model = parse_str(TEST_MODEL_WITH_EXTENSIONS, "validation-test")
        assert_model_is_valid(self, model)

    def test_validate_parsed_yaml_model_with_missing_enum_def(self):
        pattern = "unrecognized.*BehaviorType.*value.*(some_undefined_enum)"
        model = parse_str(TEST_MODEL_WITH_MISSING_ENUM_EXTENSION, "validation-test", False)
        assert_model_is_invalid(self, model, pattern)

    def test_validate_parsed_yaml_model_with_missing_data_def(self):
        pattern = "unrecognized.*field.*named.*(undefined_field)"
        model = parse_str(TEST_MODEL_WITH_MISSING_DATA_EXTENSION, "validation-test", False)
        assert_model_is_invalid(self, model, pattern)


TEST_MODEL_WITH_EXTENSIONS = """
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
          description: input description
      output:
        - name: good-morning
          type: string
      acceptance:
        - scenario: time to wake up
          when:
            - waiting 1 second
          then:
            - will say good-morning
"""

TEST_MODEL_WITH_GUN_PLUGIN_EXTENSION_VALUES = """
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
"""

TEST_MODEL_WITH_MISSING_ENUM_EXTENSION = """
model:
  name: clock
  behavior:
    - name: say goodmorning
      type: some_undefined_enum
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
"""


TEST_MODEL_WITH_MISSING_DATA_EXTENSION = """
model:
  name: clock
  behavior:
    - name: say goodmorning
      type: command
      input:
        - name: name
          type: string
          undefined_field: undefined_value
      output:
        - name: good-morning
          type: string
      acceptance:
        - scenario: time to wake up
          when:
            - waiting 1 second
          then:
            - will say good-morning
"""
