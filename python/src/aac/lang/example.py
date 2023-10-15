"""Python module for the Example class."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from dataclasses import dataclass
import attr
from typing import Optional, Any
from attr import attrib, validators

from aac.lang.examplevalue import ExampleValue


@dataclass(frozen=True)
class Example:
    """
    Collection of test values that would constitute a line in a row of examples as described in the Gherkin syntax.

    name: str - A brief description of the example data entry.
    values: list[ExampleValue]] - The values that make up the example row.
    """

    name: str = attrib(init=attr.ib(), validator=validators.instance_of(str))
    values: list[ExampleValue] = attrib(
        init=attr.ib(), validator=validators.instance_of(list[ExampleValue])
    )

    @classmethod
    def from_dict(cls, data):
        args = {}

        values_data = data.pop("values", [])
        values = [ExampleValue.from_dict(entry) for entry in values_data]
        args["values"] = values

        return cls(**args, **data)