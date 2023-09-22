import json

from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.definitions.json_schema import get_definition_json_schema

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_model_definition,
    create_field_entry,
)


class TestJsonSchema(TestCase):
    def test_get_definition_json_schema_with_schema_definition(self):
        self.maxDiff = None
        test_context = get_initialized_language_context(core_spec_only=True)

        test_sub_schema_enum_field = create_field_entry("EnumField", ["val1", "val2"])

        test_sub_schema_name = "enumSchema"
        test_sub_schema = create_schema_definition(test_sub_schema_name, fields=[test_sub_schema_enum_field])

        test_root_schema_sub_schema_field = create_field_entry("SubSchemaField", test_sub_schema_name)
        test_root_schema_primitive_field = create_field_entry("PrimitiveField", "string")
        test_root_schema_name = "myDef"
        test_root_schema = create_schema_definition(
            test_root_schema_name, fields=[test_root_schema_primitive_field, test_root_schema_sub_schema_field]
        )

        test_context.add_definitions_to_context([test_sub_schema, test_root_schema])

        expected_result = json.loads(EXPECTED_SCHEMA_JSON_SCHEMA)
        actual_result = get_definition_json_schema(test_root_schema, test_context)
        self.assertDictEqual(actual_result, expected_result)

    def test_get_definition_json_schema_with_model(self):
        self.maxDiff = None
        test_context = get_initialized_language_context(core_spec_only=True)

        test_model_name = "myModel"
        test_model = create_model_definition(test_model_name)

        test_context.add_definition_to_context(test_model)

        expected_result = json.loads(EXPECTED_MODEL_JSON_SCHEMA)
        actual_result = get_definition_json_schema(test_model, test_context)
        self.assertDictEqual(actual_result, expected_result)


EXPECTED_SCHEMA_JSON_SCHEMA = """
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "inherits": {
            "items": {
                "type": "string"
            },
            "type": "array"
        },
        "name": {
            "type": "string"
        },
        "root": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "fields": {
            "type": "array",
            "items":
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                }
            }
        },
        "requirements": {
            "properties": {
                "ids": {
                    "items": {
                        "type": "string"
                    },
                    "type": "array"
                }
            },
            "type": "object"
        },
        "validation": {
            "type": "array",
            "items":
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "arguments": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        }
    }
}
"""

EXPECTED_MODEL_JSON_SCHEMA = """
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "components": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                }
            }
        },
        "behavior": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string",
                        "enum": [
                            "PUB_SUB",
                            "REQUEST_RESPONSE",
                            "STARTUP",
                            "TIMER",
                            "LOGGING"
                        ]
                    },
                    "description": {
                        "type": "string"
                    },
                    "requirements": {
                        "properties": {
                            "ids": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "type": "object"
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "input": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "output": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "type": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "acceptance": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "scenario": {
                                    "type": "string"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "given": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "when": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                "then": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "requirements": {
            "properties": {
                "ids": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "type": "object"
        },
        "state": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                }
            }
        }
    }
}
"""
