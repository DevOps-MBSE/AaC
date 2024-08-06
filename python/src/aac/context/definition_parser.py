"""Definition Parser class for AaC, contains a load_definition function that handles loading of definition files."""
from typing import Any, Type
from enum import Enum, auto
from aac.context.language_error import LanguageError
from aac.context.definition import Definition
from aac.context.lexeme import Lexeme
from aac.context.util import get_python_module_name, get_python_class_name


class DefinitionParser():
    """Definition Parser class, responsible for loading definition files."""

    def find_definitions_by_name(self, name: str) -> list[Definition]:
        """
        Method to find a definition by name.

        Args:
            name (str): The name of the definition being searched for.

        Returns:
            The definition with the given name.
        """
        result = []
        for definition in self.context.get_definitions():
            if definition.name == name:
                result.append(definition)
        # if we didn't find any definitions in the context, check the parsed definitions
        if len(result) == 0:
            for definition in self.parsed_definitions:
                if definition.name == name:
                    result.append(definition)
        return result

    def get_location_str(self, lexeme_value: str, lexemes: list[Lexeme]) -> str:
        """
        Method to find the file name and line number for a requested Lexeme value.

        Args:
            lexeme_value (str): The Lexeme to match.
            lexemes (list[Lexeme]): A list of definition Lexemes.

        Returns:
            The file name and line number of the requested Lexeme value.
        """
        lexeme = [lexeme for lexeme in lexemes if lexeme.value == lexeme_value]
        location_str = (
            "Unable to identify source and location"  # this is the 'not found' case
        )
        if len(lexeme) == 1:  # this is the single match case
            source_str = lexeme[0].source
            line_str = lexeme[0].location.line + 1
            location_str = f"File: {source_str}  Line: {line_str}"
        elif len(lexeme) > 1:  # this is the ambiguous match case
            # check to see if location source is the same for all matches
            if all(
                [
                    lexeme[0].source == lexeme[i].source
                    for i in range(1, len(lexeme))
                ]
            ):
                source_str = lexeme[0].source
                location_str = f"File: {source_str}  Possible Lines: {', '.join([str(lex.location.line+1) for lex in lexeme])}"
            else:  # if not, just list each possible location
                location_str = "Unable to identify unique location - "
                for lex in lexeme:
                    location_str += (
                        f"File: {lex.source}  Line: {lex.location.line+1}  "
                    )
        return location_str

    def get_inheritance_parents(self, definition: Definition) -> list[Type]:
        """
        Looks up the inheritance parent classes for the given definition and returns them as a list of Python classes.

        Args:
            definition (Definition): The definition whose parent class(es) is being searched for.

        Returns:
            The parent class(es) as a list of Python classes.
        """
        inheritance_parents = []

        if "extends" in definition.structure[definition.get_root_key()]:
            for parent in definition.structure[definition.get_root_key()][
                "extends"
            ]:
                # I need to find the definition referenced by the extends
                parent_package = parent["package"]
                parent_name = parent["name"]
                parent_fully_qualified_name = ""
                try:
                    parent_fully_qualified_name = f"{get_python_module_name(parent_package)}.{get_python_class_name(parent_name)}"
                except LanguageError as e:
                    raise LanguageError(
                        f"Failed to establish parent fully qualified name from parent_package {parent_package} and parent_name {parent_name}: {e.message}", self.get_location_str(parent_name, definition.lexemes)
                    )

                if (
                    parent_fully_qualified_name
                    in self.context.context_instance.fully_qualified_name_to_class
                ):
                    inheritance_parents.append(
                        self.context.context_instance.fully_qualified_name_to_class[
                            parent_fully_qualified_name
                        ]
                    )
                else:
                    # there is a chance that processing order just means we haven't gotten to the parent yet
                    parent_definition = None
                    if (
                        parent_fully_qualified_name
                        in self.fully_qualified_name_to_definition
                    ):
                        parent_definition = self.fully_qualified_name_to_definition[
                            parent_fully_qualified_name
                        ]

                    if not parent_definition:
                        raise LanguageError(
                            f"Cannot find parent definition {parent_fully_qualified_name} for {definition.name}",
                            self.get_location_str(parent_name, definition.lexemes),
                        )

                    if parent_definition.get_root_key() == "schema":
                        inheritance_parents.append(
                            self.create_schema_class(parent_definition)
                        )
                    else:
                        # AaC only supports schema inheritance
                        raise LanguageError(
                            f"AaC extension is only supported for schema.  Unable to create parent class with AaC root: {parent_definition.get_root_key()}",
                            self.get_location_str(parent_name, definition.lexemes),
                        )

        return inheritance_parents

    def create_enum_class(self, enum_definition: Definition) -> Enum:
        """
        Creates an enum class from a given enum definition.

        Args:
            enum_definition (Definition): An enum definition to convert to a class.

        Returns:
            The created class.
        """
        if enum_definition.get_root_key() != "enum":
            raise LanguageError(
                f"Definition {enum_definition.name} is not an enum",
                self.get_location_str(
                    enum_definition.get_root_key(), enum_definition.lexemes
                )
            )

        fully_qualified_name = enum_definition.get_fully_qualified_name()
        if (
            fully_qualified_name
            in self.context.context_instance.fully_qualified_name_to_class
        ):
            # we've already created the class, so nothing to do here
            return self.context.context_instance.fully_qualified_name_to_class[
                fully_qualified_name
            ]

        # Note:  trying to allow extension with Enums fails, so I just removed it
        #        but we can revisit and try to find a solution in the future if needed

        values = {}
        if "values" in enum_definition.structure["enum"]:
            for value in enum_definition.structure["enum"]["values"]:
                values[value] = auto()
        # create the enum class
        instance_class = None
        try:
            instance_class = Enum(
                enum_definition.get_python_class_name(),
                values,
                module=enum_definition.get_python_module_name(),
            )
        except LanguageError as e:
            raise LanguageError(
                f"Failed to create Enum instance_class for {enum_definition.name}: {e.message}",
                self.get_location_str(enum_definition.name, enum_definition.lexemes),
            )
        self.context.context_instance.fully_qualified_name_to_class[
            fully_qualified_name
        ] = instance_class
        return instance_class

    def add_field_to_class(self, field: dict, instance_class: Type, schema_definition: Definition) -> Type:
        """
        Creates an attribute within the instance class and adds the field name and type to it.

        Args:
            field (dict): The field being loaded into the instance class.
            instance_class (Type): The instance class being loaded with field definitions.
            schema_definition (Definition): The schema definition containing the fields being iterated through and loaded.

        Returns:
            the instance class after being loaded with field definitions.
        """
        field_name = field["name"]
        field_type = field["type"]
        is_list = False

        clean_field_type = field_type
        if field_type.endswith("[]"):
            is_list = True
            clean_field_type = field_type[:-2]
        if "(" in clean_field_type:
            clean_field_type = clean_field_type[: clean_field_type.find("(")]

        # let's make sure the type of the field is known, or create it if it's not
        potential_definitions = self.find_definitions_by_name(clean_field_type)
        if len(potential_definitions) != 1:
            if len(potential_definitions) == 0:
                raise LanguageError(
                    f"Could not find AaC definition for type {clean_field_type} while loading {schema_definition.name}",
                    self.get_location_str(field_type, schema_definition.lexemes),
                )
            else:
                raise LanguageError(
                    f"Discovered multiple AaC definitions for type {clean_field_type} while loading {schema_definition.name}.  You may need to add a package name to differentiate.",
                    self.get_location_str(field_type, schema_definition.lexemes),
                )

        parsed_definition = potential_definitions[0]

        self.create_schema_class(parsed_definition)

        # since python is dynamically typed, we really don't have to worry about setting a type when we create the field
        # we just need to make sure a reasonable default value is used, so for us that means an empty list or None
        # Question:  is there ever a case where we may need a dict value?
        if is_list:
            setattr(instance_class, field_name, [])
        else:
            setattr(instance_class, field_name, None)
        return instance_class

    def create_instance_class(self, inheritance_parents: list, schema_definition: Definition) -> Type:
        """
        Method to create an instance class type for the given definition.

        Args:
            inheritance_parents (list[Type]): Types that this definition inherits from.
            schema_definition (Definition): The definition being converted to an instance class.

        Returns:
            The created instance class.
        """
        if len(inheritance_parents) == 0:
            base_content = [object]
        else:
            base_content = inheritance_parents

        try:
            instance_class = type(
                schema_definition.get_python_class_name(),
                tuple(base_content),
                {"__module__": schema_definition.get_python_module_name()}
            )
        except LanguageError as e:
            raise LanguageError(
                f"Failed to create instance_class for {schema_definition.name}: {e.message}",
                self.get_location_str(
                    schema_definition.name, schema_definition.lexemes
                )
            )
        return instance_class

    def create_schema_class(self, schema_definition: Definition) -> Type:
        """
        Creates a schema class from a given schema definition.

        Args:
            schema_definition (Definition): A schema definition to convert to a class.

        Returns:
            The created class.
        """

        fully_qualified_name = schema_definition.get_fully_qualified_name()
        if schema_definition.get_root_key() == "primitive":
            # this is a primitive, so there's no structure to create, just return the python type
            return eval(self.primitive_name_to_py_type[schema_definition.name])
        elif schema_definition.get_root_key() == "enum":
            # this is an enum, so create the enum class
            return self.create_enum_class(schema_definition)
        elif schema_definition.get_root_key() != "schema":
            raise LanguageError(
                f"Definition {schema_definition.name} is not a schema",
                self.get_location_str(
                    schema_definition.get_root_key(), schema_definition.lexemes
                )
            )

        if (
            fully_qualified_name
            in self.context.context_instance.fully_qualified_name_to_class
        ):
            # we've already created the class, so nothing to do here
            return self.context.context_instance.fully_qualified_name_to_class[
                fully_qualified_name
            ]

        inheritance_parents = self.get_inheritance_parents(schema_definition)
        instance_class = self.create_instance_class(inheritance_parents, schema_definition)

        # now add the fields to the class
        for field in schema_definition.structure["schema"]["fields"]:
            instance_class = self.add_field_to_class(field, instance_class, schema_definition)

        # finally store the class in the context
        self.context.context_instance.fully_qualified_name_to_class[
            fully_qualified_name
        ] = instance_class
        return instance_class

    def create_object_instance(self, type_class: Type, fields: dict) -> Any:
        """
        Creates an instance object from the given fields.

        Args:
            type_class (Type): The class created from the field type.
            fields (dict): Given fields to create instances from.

        Returns:
            The created instance object.
        """
        result = type_class()
        for field_name, field_value in fields.items():
            setattr(result, field_name, field_value)
        return result

    def get_defined_fields(self, package: str, name: str) -> list[str]:
        """
        Returns a list of defined fields for the given definition.

        Args:
            package (str): The definition package.
            name (str): The definition name.

        Returns:
            A list of definition fields.
        """
        result = []
        defining_definition = None
        for definition in self.context.get_definitions() + self.parsed_definitions:
            if definition.name == name and definition.package == package:
                defining_definition = definition
                break
        if (
            "extends"
            in defining_definition.structure[defining_definition.get_root_key()]
        ):
            for parent in defining_definition.structure[
                defining_definition.get_root_key()
            ]["extends"]:
                result.extend(self.get_defined_fields(parent["package"], parent["name"]))
        if "fields" in defining_definition.structure[definition.get_root_key()]:
            result.extend(
                [
                    field["name"]
                    for field in definition.structure[definition.get_root_key()][
                        "fields"
                    ]
                ]
            )
        return result

    def populate_sub_fields(self, subfields: dict, defining_definition: Definition, item: dict, lexemes: list[Lexeme]) -> dict:
        """
        Method used to populate sub-fields in an instance class field.

        Args:
            subfields (dict): dictionary containing relevant sub-fields.
            defining_definition (Definition): The overall definition containing the field.
            item (dict): The current field definition which contains sub-fields.
            lexemes (List[Lexeme]): A list of definition Lexemes.

        Returns:
            The populated dictionary of sub-fields.
        """
        for subfield in defining_definition.structure["schema"][
            "fields"
        ]:
            subfield_name = subfield["name"]
            subfield_type = subfield["type"]
            subfield_is_required = False
            if "is_required" in subfield:
                subfield_is_required = subfield["is_required"]
            subfield_value = None
            if subfield_name in item:
                subfield_value = item[subfield_name]
            else:
                if "default" in subfield:
                    # let's see if we need to cast the value
                    subfield_default_str = subfield["default"]
                    if isinstance(subfield_default_str, str):
                        type_map = {
                            "int": int,
                            "number": float,
                            "bool": lambda x: x.lower()
                            in ("yes", "true", "t", "1"),
                            "string": str,
                        }
                        if subfield_type in type_map:
                            subfield_value = type_map[
                                subfield_type
                            ](subfield_default_str)
                    else:
                        subfield_value = subfield_default_str
            # we need to eliminate previously covered lexemes, so go through the list until we find subfield_name then add it and everything else
            found = False
            sub_lexemes = []
            for lex in lexemes:
                if lex.value == subfield_name:
                    found = True
                    sub_lexemes.append(lex)
                if found:
                    sub_lexemes.append(lex)
            subfields[subfield_name] = self.create_field_instance(
                subfield_name,
                subfield_type,
                subfield_is_required,
                subfield_value,
                sub_lexemes,
            )
        return subfields

    def field_instance_creator_list(self, lexemes: list, field_value: Any, field_name: str, defining_definition: Definition, instance: list, instance_class: Type) -> list:
        """
        Method to create instance fields from list type fields.

        Args:
            lexemes (List[Lexeme]): A list of definition Lexemes.
            field_value (Any): Value stored in the field.
            field_name (str): The name of the field.
            defining_definition (Definition): Definition containing the field being checked.
            instance (list[Any]: The instance that will contain the created field)
            instance_class (Type): The instance type class

        Returns:
            The updated instance containing the created field.
        """
        for item in field_value:
            if not isinstance(item, dict):
                raise LanguageError(
                    f"Invalid parsed value for field '{field_name}'.  Expected type 'dict', but found '{type(item)}'. Value = {item}",
                    self.get_location_str(field_name, lexemes),
                )
            # go through the fields and create instances for each
            subfields = {}
            if "fields" not in defining_definition.structure["schema"]:
                raise LanguageError(
                    f"Schema '{defining_definition.name}' does not contain any fields.",
                    self.get_location_str(field_name, lexemes),
                )

            # make sure there are no undefined fields
            defined_field_names = self.get_defined_fields(
                defining_definition.package, defining_definition.name
            )
            item_field_names = [field for field in item.keys()]
            for item_field_name in item_field_names:
                if item_field_name not in defined_field_names:
                    raise LanguageError(
                        f"Found undefined field name '{item_field_name}' when expecting {defined_field_names} as defined in {defining_definition.name}",
                        self.get_location_str(item_field_name, lexemes),
                    )
            subfields = self.populate_sub_fields(subfields, defining_definition, item, lexemes)

            instance.append(
                self.create_object_instance(instance_class, subfields)
            )
        return instance

    def field_instance_creator_not_list(self, lexemes: list, field_value: Any, field_name: str, defining_definition: Definition, instance: list, instance_class: Type) -> list:
        """
        Method to create instance fields from non-list type fields.

        Args:
            lexemes (List[Lexeme]): A list of definition Lexemes.
            field_value (Any): Value stored in the field.
            field_name (str): The name of the field.
            defining_definition (Definition): Definition containing the field being checked.
            instance (list[Any]: The instance that will contain the created field)
            instance_class (Type): The instance type class

        Returns:
            The updated instance containing the created field
        """
        defined_field_names = self.get_defined_fields(
            defining_definition.package, defining_definition.name
        )
        item_field_names = [field for field in field_value.keys()]
        for item_field_name in item_field_names:
            if item_field_name not in defined_field_names:
                raise LanguageError(
                    f"Found undefined field name '{item_field_name}' when expecting {defined_field_names} as defined in {defining_definition.name}",
                    self.get_location_str(item_field_name, lexemes),
                )

        subfields = {}
        if "fields" not in defining_definition.structure["schema"]:
            raise LanguageError(
                f"Schema '{defining_definition.name}' does not contain any fields.",
                self.get_location_str(field_name, lexemes),
            )
        subfields = self.populate_sub_fields(subfields, defining_definition, field_value, lexemes)
        instance = self.create_object_instance(instance_class, subfields)
        return instance

    def field_instance_check(self, is_list: bool, field_value: Any, field_name: str, is_required: bool, lexemes: list[Lexeme], defining_definition: Definition, instance_class: Type) -> list:
        """
        Method used to check if a field is a list, and to call the corresponding field instance creator method.

        Args:
            is_list (bool): Boolean value determining if the field type is a list.
            field_value (Any): Value stored in the field.
            field_name (str): The name of the field.
            lexemes (List[Lexeme]): A list of definition Lexemes.
            defining_definition (Definition): Definition containing the field being checked.
            instance_class (Type): The class type of the instance being created.

        Returns:
            The created instance list.
        """
        if is_list:
            instance = []
            if not field_value:
                if is_required:
                    raise LanguageError(f"Missing required field {field_name}")
            else:
                if not isinstance(field_value, list):
                    if is_required:
                        raise LanguageError(
                            f"Invalid parsed value for field '{field_name}'.  Expected type 'list', but found '{type(field_value)}'.  Value = {field_value}",
                            self.get_location_str(field_name, lexemes),
                        )
                    else:
                        return instance
                instance = self.field_instance_creator_list(lexemes, field_value, field_name, defining_definition, instance, instance_class)
        else:
            instance = None
            if not field_value:
                if is_required:
                    raise LanguageError(
                        f"Missing required field {field_name}",
                        self.get_location_str(field_name, lexemes),
                    )
                else:
                    return instance
            if not isinstance(field_value, dict):
                # this is a complex type defined by a schema, with a field value so it should be a dict
                raise LanguageError(
                    f"Invalid parsed value for field '{field_name}'.  Expected type 'dict', but found '{type(field_value)}'.  Value = {field_value}",
                    self.get_location_str(field_name, lexemes),
                )

            # make sure there are no undefined fields
            instance = self.field_instance_creator_not_list(lexemes, field_value, field_name, defining_definition, instance, instance_class)
        return instance

    def primitive_field_value_check(self, is_list: bool, field_value: Any, field_name: str, is_required: bool, lexemes: list, defining_definition: Definition) -> Any:
        """
        Method used to ensure primitive type field definitions have valid values.

        Args:
            is_list (bool): Boolean value determining if the field type is a list.
            field_value (Any): Value stored in the field.
            field_name (str): The name of the field.
            is_required (bool): Boolean value determining if the field is required.
            lexemes (List[Lexeme]): A list of definition Lexemes.
            defining_definition (Definition): Definition containing the field being checked.

        Returns:
            The content of the primitive type field value.
        """
        python_type = defining_definition.structure["primitive"]["python_type"]
        if not field_value:
            if is_required:
                raise LanguageError(message=f"Missing required field {field_name}.", location=None)
            if is_list:
                field_value = []
        elif is_list:
            for item in field_value:
                if not isinstance(item, eval(python_type)):
                    raise LanguageError(
                        message=f"Invalid value for field '{field_name}'.  Expected type '{python_type}', but found '{type(item)}'",
                        location=self.get_location_str(field_value, lexemes),
                    )
        else:
            if "Any" != python_type:
                if not isinstance(field_value, eval(python_type)):
                    raise LanguageError(
                        f"Invalid value for field '{field_name}'.  Expected type '{python_type}', but found '{type(field_value)}'",
                        self.get_location_str(field_value, lexemes),
                    )
        return field_value

    def enum_field_value_check(self, is_list: bool, field_value: Any, field_name: str, lexemes: list, defining_definition: Definition) -> list:
        """
        Method used to ensure enum type field definitions have valid values.

        Args:
            is_list (bool): Boolean value determining if the field type is a list.
            field_value (Any): Value stored in the field.
            field_name (str): The name of the field.
            lexemes (List[Lexeme]): A list of definition Lexemes.
            defining_definition (Definition): Definition containing the field being checked.

        Returns:
            The list of valid enum field values.
        """
        enum_class = self.context.context_instance.fully_qualified_name_to_class[
            defining_definition.get_fully_qualified_name()
        ]
        if not enum_class:
            enum_class = self.create_enum_class(defining_definition)
        if is_list:
            result = []
            for item in field_value:
                if not isinstance(item, str):
                    raise LanguageError(
                        f"Invalid value for field '{field_name}'.  Expected type 'str', but found '{type(item)}'",
                        self.get_location_str(field_name, lexemes),
                    )
                try:
                    result.append(getattr(enum_class, item))
                except ValueError:
                    raise LanguageError(
                        f"{item} is not a valid value for enum {defining_definition.name}",
                        self.get_location_str(item, lexemes),
                    )
            return result
        else:
            if not field_value:
                return [None]
            try:
                return self.context.create_aac_enum(
                    defining_definition.get_fully_qualified_name(), field_value
                )
            except ValueError:
                raise LanguageError(
                    f"{field_value} is not a valid value for enum {defining_definition.name}",
                    self.get_location_str(field_value, lexemes),
                )

    def schema_field_value_check(self, is_list, field_value, field_name: str, is_required, lexemes, defining_definition) -> list:
        """
        Method used to ensure schema type field definitions have valid values.

        Args:
            is_list (bool): Boolean value determining if the field type is a list.
            field_value (Any): Value stored in the field.
            field_name (str): The name of the field.
            lexemes (List[Lexeme]): A list of definition Lexemes.
            defining_definition (Definition): Definition containing the field being checked.

        Returns:
            The List of valid schema defined field values.
        """
        field_fully_qualified_name = (
            defining_definition.get_fully_qualified_name()
        )
        instance_class = self.context.context_instance.fully_qualified_name_to_class[
            field_fully_qualified_name
        ]
        if not instance_class:
            if defining_definition.get_root_key() == "schema":
                instance_class = self.create_schema_class(defining_definition)
            else:
                raise LanguageError(
                    f"Unable to process AaC definition of type {field_fully_qualified_name} with root {defining_definition.get_root_key()}",
                    self.get_location_str(field_name, lexemes),
                )
        instance = self.field_instance_check(is_list, field_value, field_name, is_required, lexemes, defining_definition, instance_class)

        return instance

    def create_field_instance(
        self,
        field_name: str,
        field_type: str,
        is_required: bool,
        field_value: Any,
        lexemes: list[Lexeme],
    ) -> Any:
        """
        Adds an entry to the instance attribute of a definition for the given field.

        Args:
            field_name (str): Name of the field.
            field_type (str): Type of the field.
            is_required (bool): Contents of the is_required field for the specified field.
            field_value (Any): The value for the specified field.
            lexemes (list[Lexeme]): A list of definition Lexemes.

        Returns:
            The instance field value.
        """
        is_list = False
        clean_field_type = field_type
        if field_type.endswith("[]"):
            is_list = True
            clean_field_type = field_type[:-2]
        if "(" in clean_field_type:
            clean_field_type = clean_field_type[: clean_field_type.find("(")]

        # now get the defining definition from the clean_field_type
        defining_definitions = self.find_definitions_by_name(clean_field_type)
        if not defining_definitions or len(defining_definitions) == 0:
            raise LanguageError(
                f"Could not find definition for '{clean_field_type}'.",
                self.get_location_str(field_type, lexemes),
            )
        elif len(defining_definitions) > 1:
            raise LanguageError(
                f"Found multiple definitions for '{clean_field_type}'.",
                self.get_location_str(field_type, lexemes),
            )
        defining_definition = defining_definitions[0]

        if defining_definition.get_root_key() == "primitive":
            # this is a primitive, so ensure the parsed value aligns with the type and return it
            return self.primitive_field_value_check(is_list, field_value, field_name, is_required, lexemes, defining_definition)

        elif defining_definition.get_root_key() == "enum":
            # this is an enum, so ensure the parsed value aligns with the type and return it
            return self.enum_field_value_check(is_list, field_value, field_name, lexemes, defining_definition)

        else:  # this isn't a primitive and isn't an enum, so it must be a schema
            return self.schema_field_value_check(is_list, field_value, field_name, is_required, lexemes, defining_definition)

    def create_definition_instance(self, definition: Definition) -> Any:
        """
        Populates the instance field of a given definition.

        Args:
            definition (Definition): The given definition being populated.

        Returns:
            The populated instance for the given definition.
        """
        instance = None

        defining_definition = None
        for item in self.context.get_definitions() + self.parsed_definitions:
            if item.get_root_key() == "schema":
                if "root" in item.structure["schema"]:
                    if (
                        definition.get_root_key()
                        == item.structure["schema"]["root"]
                    ):
                        defining_definition = item

        if not defining_definition:
            raise LanguageError(
                f"Could not find definition for {definition.name} with root {definition.get_root_key()}",
                self.get_location_str(definition.get_root_key(), definition.lexemes),
            )

        if defining_definition.get_root_key() == "schema":
            # since schemas are how we define "all the things" the root key of the defining definition should be 'schema'
            self.create_schema_class(defining_definition)
        else:
            raise LanguageError(
                f"Definition for root key '{defining_definition.get_root_key()}' is not a Schema.",
                self.get_location_str(definition.get_root_key(), definition.lexemes),
            )

        instance = self.create_field_instance(
            "root",
            defining_definition.name,
            True,
            definition.structure[definition.get_root_key()],
            definition.lexemes,
        )

        definition.instance = instance
        return instance

    # Start the load_definition function code here
    def load_definitions(
        self, context, parsed_definitions: list[Definition]
    ) -> list[Definition]:
        """
        Loads the given definitions into the context and populates the instance with a python object.

        Args:
            context (LanguageContext): An instance of the active LanguageContext.
            parsed_definitions: (list[Definition]): The parsed contents of a definition file.

        Returns:
            The parsed definitions to load into the LanguageContext.
        """

        # Maintainer note:  Yes, this function is a bit of a monster...sorry about that.
        # I wanted to keep all this stuff together because if it all works out this should be the
        # only place where we have to deal with navigating the structure of the definitions and
        # not using the python objects.  In order for this to work, any changes in here should
        # avoid the use of he definition instance...other than actually creating it.
        result = []
        schema_defs_by_root = {}
        self.context = context
        self.parsed_definitions = parsed_definitions
        self.primitive_name_to_py_type = {
            definition.name: definition.structure["primitive"]["python_type"]
            for definition in self.parsed_definitions + self.context.get_definitions()
            if definition.get_root_key() == "primitive"
        }
        self.fully_qualified_name_to_definition = {
            definition.get_fully_qualified_name(): definition
            for definition in self.parsed_definitions + self.context.get_definitions()
            if "package" in definition.structure[definition.get_root_key()]
        }

        for definition in self.context.get_definitions():
            if definition.get_root_key() == "schema":
                if definition.instance.root:
                    schema_defs_by_root[definition.instance.root] = definition

        for definition in self.parsed_definitions:
            # create and register the instance
            self.create_definition_instance(definition)
            definition.source.is_loaded_in_context = True
            result.append(definition)
            self.context.context_instance.definitions.add(definition)
            self.context.context_instance.fully_qualified_name_to_definition[
                f"{definition.package}.{definition.name}"
            ] = definition

        return result
