"""Python module for the Schema class."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from dataclasses import dataclass
import attr
from typing import Optional, Any
from attr import attrib, validators

from aac.lang.aactype import AacType


from aac.lang.schemaextension import SchemaExtension
from aac.lang.field import Field
from aac.lang.schemaconstraintassignment import SchemaConstraintAssignment


@dataclass(frozen=True)
class Schema(AacType):
    """
    A definition that defines the schema/structure of data.

    extends: list[SchemaExtension]] - A list of Schema definition names that this definition inherits from.
    modifiers: list[str] - A means of further defining the schema and how it can be used within the model.
    root: Optional[str] - The root key to use when declaring an instance of the type in yaml/aac files.
    fields: list[Field]] - A list of fields that make up the definition.
    requirements: list[str] - A list of requirements associated with this schema.
    constraints: list[SchemaConstraintAssignment]] -
    """

    extends: list[SchemaExtension] = attrib(
        init=attr.ib(), validator=validators.instance_of(list[SchemaExtension])
    )
    modifiers: list[str] = attrib(
        init=attr.ib(), validator=validators.instance_of(list[str])
    )
    root: Optional[str] = attrib(
        init=attr.ib(), validator=validators.optional(validators.instance_of(str))
    )
    fields: list[Field] = attrib(
        init=attr.ib(), validator=validators.instance_of(list[Field])
    )
    requirements: list[str] = attrib(
        init=attr.ib(), validator=validators.instance_of(list[str])
    )
    constraints: list[SchemaConstraintAssignment] = attrib(
        init=attr.ib(),
        validator=validators.instance_of(list[SchemaConstraintAssignment]),
    )

    @classmethod
    def from_dict(cls, data):
        args = {}

        extends_data = data.pop("extends", [])
        extends = [SchemaExtension.from_dict(entry) for entry in extends_data]
        args["extends"] = extends

        modifiers = data.pop("modifiers", [])
        args["modifiers"] = modifiers

        root = data.pop("root", None)
        args["root"] = root

        fields_data = data.pop("fields", [])
        fields = [Field.from_dict(entry) for entry in fields_data]
        args["fields"] = fields

        requirements = data.pop("requirements", [])
        args["requirements"] = requirements

        constraints_data = data.pop("constraints", [])
        constraints = [
            SchemaConstraintAssignment.from_dict(entry) for entry in constraints_data
        ]
        args["constraints"] = constraints

        return cls(**args, **data)