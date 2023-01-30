"""
This module provides string constants for strings used in the Core AaC Spec.

These values aren't expected to change often; it's expected that any deviation
between these values and the core spec will be caught by testing.
"""

# Root Keys
ROOT_KEY_IMPORT = "import"
ROOT_KEY_ENUM = "enum"
ROOT_KEY_SCHEMA = "schema"
ROOT_KEY_MODEL = "model"
ROOT_KEY_USECASE = "usecase"
ROOT_KEY_EXTENSION = "ext"
ROOT_KEY_VALIDATION = "validation"

# Common Definition Field Names
DEFINITION_FIELD_ADD = "add"
DEFINITION_FIELD_ARGUMENTS = "arguments"
DEFINITION_FIELD_BEHAVIOR = "behavior"
DEFINITION_FIELD_DESCRIPTION = "description"
DEFINITION_FIELD_EXTENSION_ENUM = "enumExt"
DEFINITION_FIELD_EXTENSION_SCHEMA = "schemaExt"
DEFINITION_FIELD_FIELDS = "fields"
DEFINITION_FIELD_INHERITS = "inherits"
DEFINITION_FIELD_NAME = "name"
DEFINITION_FIELD_REQUIRED = "required"
DEFINITION_FIELD_TYPE = "type"
DEFINITION_FIELD_VALIDATION = "validation"
DEFINITION_FIELD_VALUES = "values"

# Core AaC Definition Names
DEFINITION_NAME_PRIMITIVES = "Primitives"
DEFINITION_NAME_ROOT = "root"
DEFINITION_NAME_SCHEMA = "schema"
DEFINITION_NAME_MODEL = "model"
DEFINITION_NAME_FIELD = "Field"

# Core AaC Primitive Types
PRIMITIVE_TYPE_STRING = "string"
PRIMITIVE_TYPE_INT = "int"
PRIMITIVE_TYPE_NUMBER = "number"
PRIMITIVE_TYPE_BOOL = "bool"
PRIMITIVE_TYPE_DATE = "date"
PRIMITIVE_TYPE_FILE = "file"
PRIMITIVE_TYPE_REFERENCE = "reference"
