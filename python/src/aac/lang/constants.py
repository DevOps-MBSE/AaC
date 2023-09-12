"""
This module provides string constants for strings used in the Core AaC Spec.

These values aren't expected to change often; it's expected that any deviation
between these values and the core spec will be caught by testing.
"""

# Root Keys
ROOT_KEY_COMMAND_GROUP = "command_group"
ROOT_KEY_ENUM = "enum"
ROOT_KEY_EXTENSION = "ext"
ROOT_KEY_IMPORT = "import"
ROOT_KEY_MODEL = "model"
ROOT_KEY_PLUGIN = "plugin"
ROOT_KEY_SCHEMA = "schema"
ROOT_KEY_SPECIFICATION = "spec"
ROOT_KEY_USECASE = "usecase"
ROOT_KEY_VALIDATION = "validation"

# Common Definition Field Names
DEFINITION_FIELD_ACCEPTANCE = "acceptance"
DEFINITION_FIELD_ACTION = "action"
DEFINITION_FIELD_ADD = "add"
DEFINITION_FIELD_ARGUMENTS = "arguments"
DEFINITION_FIELD_BEHAVIOR = "behavior"
DEFINITION_FIELD_COMMANDS = "commands"
DEFINITION_FIELD_COMPONENTS = "components"
DEFINITION_FIELD_DEFINITION_SOURCES = "definitionSources"
DEFINITION_FIELD_DEFINITION_VALIDATIONS = "definitionValidations"
DEFINITION_FIELD_DESCRIPTION = "description"
DEFINITION_FIELD_DISPLAY = "display"
DEFINITION_FIELD_EXTENSION_ENUM = "enumExt"
DEFINITION_FIELD_EXTENSION_SCHEMA = "schemaExt"
DEFINITION_FIELD_FIELDS = "fields"
DEFINITION_FIELD_FILES = "files"
DEFINITION_FIELD_GIVEN = "given"
DEFINITION_FIELD_GROUP = "group"
DEFINITION_FIELD_HELP_TEXT = "helpText"
DEFINITION_FIELD_IMPORT = "import"
DEFINITION_FIELD_INHERITS = "inherits"
DEFINITION_FIELD_INPUT = "input"
DEFINITION_FIELD_NAME = "name"
DEFINITION_FIELD_OUTPUT = "output"
DEFINITION_FIELD_PARTICIPANTS = "participants"
DEFINITION_FIELD_PRIMITIVE_VALIDATIONS = "primitiveValidations"
DEFINITION_FIELD_REQUIRED = "required"
DEFINITION_FIELD_ROOT = "root"
DEFINITION_FIELD_SCENARIO = "scenario"
DEFINITION_FIELD_SOURCE = "source"
DEFINITION_FIELD_STATE = "state"
DEFINITION_FIELD_STEP = "step"
DEFINITION_FIELD_STEPS = "steps"
DEFINITION_FIELD_TAGS = "tags"
DEFINITION_FIELD_TARGET = "target"
DEFINITION_FIELD_THEN = "then"
DEFINITION_FIELD_TYPE = "type"
DEFINITION_FIELD_VALIDATION = "validation"
DEFINITION_FIELD_VALIDATIONS = "validations"
DEFINITION_FIELD_VALUES = "values"
DEFINITION_FIELD_WHEN = "when"

# Core AaC Definition Names
DEFINITION_NAME_BEHAVIOR = "Behavior"
DEFINITION_NAME_BEHAVIOR_TYPE = "BehaviorType"
DEFINITION_NAME_ENUM = "Enum"
DEFINITION_NAME_EXTENSION = "Extension"
DEFINITION_NAME_FIELD = "Field"
DEFINITION_NAME_MODEL = "Model"
DEFINITION_NAME_PRIMITIVES = "Primitives"
DEFINITION_NAME_REQUIREMENT = "Requirement"
DEFINITION_NAME_REQUIREMENT_REFERENCE = "RequirementReference"
DEFINITION_NAME_ROOT = "Root"
DEFINITION_NAME_SCENARIO = "Scenario"
DEFINITION_NAME_SCHEMA = "Schema"
DEFINITION_NAME_SPECIFICATION = "Specification"
DEFINITION_NAME_USECASE = "Usecase"
DEFINITION_NAME_VALIDATION = "Validation"
DEFINITION_NAME_VALIDATION_REFERENCE = "ValidationReference"

# Core AaC Primitive Types
PRIMITIVE_TYPE_BOOL = "bool"
PRIMITIVE_TYPE_DATE = "date"
PRIMITIVE_TYPE_DIRECTORY = "directory"
PRIMITIVE_TYPE_FILE = "file"
PRIMITIVE_TYPE_INT = "int"
PRIMITIVE_TYPE_NUMBER = "number"
PRIMITIVE_TYPE_REFERENCE = "reference"
PRIMITIVE_TYPE_STRING = "string"

# Core AaC Behavior Types
BEHAVIOR_TYPE_PUBLISH_SUBSCRIBE = "PUB_SUB"
BEHAVIOR_TYPE_REQUEST_RESPONSE = "REQUEST_RESPONSE"
BEHAVIOR_TYPE_STARTUP = "STARTUP"
BEHAVIOR_TYPE_TIMER = "TIMER"
