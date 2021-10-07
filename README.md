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


## Updates done over the weekend
I've spent some time exploring ideas and made some significant changes.  I've pretty much rewritten the whole thing, but I have preserved the original code in the orig folder.
1) Changed to a (mostly) self defining modeling capabiliy.
    - Initially I was validating YAML models using a JSON schema.  This worked pretty well, but required learning of JSON schemas to extent the capability.
    - Now there is a YAML definition of the AaC modelling language, using the AaC modeling language.
    - There are some "hard coded" core concepts now baked into the validation.
        - The representation of import, data, and model (top level) are hard coded and cannot be changed.
        - The existance of a model item is hard coded, but the content is validated using the YAML model in AaC.yaml
        - All data types within model are dynamic...although I'm sure certain things will break if changes are made.
        - Nothing is hardened...or resiliently designed.
        - There are no real tests...just sample models that can be ran.
2) I've modeled the AaC CLI...but it's just a model, not used for anything.
    - I've found this useful to reason about the design of the AaC model structure and tool implementation.
    - I have hand built the AaC CLI based on the AaC CLI model as best I could.
    - Hopefully this will allow me to experiment with code generation in the future.  I'd like to generate the CLI base applicaiton if possible.
3) Not really a change, but I've stuck with Python
    - I am not a Python developer.  Any Pythonistas out there will have plenty of opportunity to make fun of what I've done here.
    - I have enjoyed learning Python as I went through this.
4) Added use cases
    - There is a new root type called usecase
    - Parsing and validation works (good enough for now anyway)
    - Changed puml to include two commands:  puml-component generates component diagram from a model, puml-sequence generates sequence diagram from a usecase
4) There's a lot of things I've considered doing but haven't
    - Create a built-in representation of hashmaps for use in modeling (but maybe I'm just too reliant on Python dict types now)
    - Attempt to only use the root data type as the sole "hard coded" item and truely make the model dog food itself
    - Refactor and build real unit tests / acceptance tests
    - Auto-generate Cucumber feature files from a scenario.
    - Auto-generate PlantUML sequence diagrams.
    - Auto-generate RESTful service infrastructure for request-response behaviors
    - Create an extension solution in the model to modify built-in data types and enums
    - Create a XOR validation for fields in a data model (not convinced this is a good idea)
    - Create a way to reference other definitions within the model for additional validation (i.e. data.required value must be in data.fields.name)
    - Auto-generate documentation (probably need alot more description fields in the model definition to capture content)
    - Create a way to reference external items (ex: requirement, story, spec, etc)


## Python setup

Set up your virtual environment:

```bash
$ python3.9 -m venv .env
$ source .env/bin/activate
```

To install project and development dependencies, run this:

```bash
$ pip install -r dev-requirements.txt
```

To install only project dependencies, run this:

```bash
$ pip install -r requirements.txt
```
