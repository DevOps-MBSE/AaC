# Architecture-as-Code

This is a scratch space to explore concepts and is not intended to create anything useful at this time.

Potential Use Cases:
1) Model the logical decomposition of a system
    - User creates a model representing the entire system
    - User creates a model for a nested portion of the system
    - User specifies the nested system portion is contained within the system model
    - User creates another level of nexted models using the same mechanism
2) Model abstract and concrete portions of a system
    - User creates a model representing the entire system
    - User creates multiple models of nested portions of the system
    - User specifies the nested portions as concrete representations (i.e. not to be further decomosed)
    - User gets an error if attempting to model a further nested portion of a concrete model element
3) Model simple data for a system
    - User has defined a model of a system or portion of a system
    - User creates a data model 
    - User creates data elements as a list of primitives (int, float, string, bool)
    - User specifies the cardinality of each data element (standard (0-1), required (1), list(0-N))
4) Model complex data for a system
    - User has defined a data model using primitive types
    - User creates a new data model
    - User creates a data element of the named type from the previously defined data model
    - User specifies the cardinality of each data element (standard (0-1), required (1), list(0-N))
5) Model an interface for a system
    - User has a defined system model and data model
    - User adds a trigger to the system model
    - User defines the trigger to be onReceive and references the data type from the data model


## Example System Model (Point of Sale)
The CONOPS starts with the product scanner identifying a barcode and publishing the scan result.  The product catalog 
subscribes to this, looks up the product info, and publishes it.

See ./point-of-sale.yaml




"uses": {
                "description": "",
                "type": "array",
                "items": {"items": { "$ref": "#/$defs/use" }},
                "minItems": 0,
                "uniqueItems": true
            },

            "prefixItems": [
              { "type": "string" },
              { "type": "string" }
            ],
            "items": false


            "refs": {
                        "description": "",
                        "type": "array",
                        "items": {"items": { "$ref": "#/$defs/ref" }},
                        "minItems": 0,
                        "uniqueItems": true
                    },



## Python setup
pip install pyyaml
pip install jsonschema
pip install nose2  (this is a unit test runner)