"""The AaC AaC primitive constraints plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)
from aac.in_out.files.aac_file import AaCFile
from aac.context.source_location import SourceLocation
from aac.context.language_context import LanguageContext

from os import linesep
from datetime import datetime


plugin_name = "AaC primitive constraints"


def check_bool(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check bool constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    if not isinstance(value, bool):
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"{value} is not a valid bool value.",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check bool", status, messages)


def check_date(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check date constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    try:
        datetime.fromisoformat(str(value))
    except ValueError as error:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"Failed to parse the date time string '{value}' with error: '{error}'",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check date", status, messages)


def check_directory(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check directory constraint."""

    # I think this should work fine
    return check_file(value, type_declaration, source, location)


def check_file(  # noqa: C901
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check file constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    if not isinstance(value, str):
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"{value} is not a valid file path. Value should be string but received {type(value)}",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)
        return ExecutionResult(plugin_name, "Check file", status, messages)

    # I tried to do this with a regex but got frustrated and gave up.  For some reason, the complex regex the AI generated for me would just run forever when matching.
    # So here's a brute force approach.
    valid_separators = ["/", "\\"]
    item = ""
    path_entries = []
    valid_path_characters = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    )
    for character in value:
        if character in valid_separators:
            if item != "":
                path_entries.append(item)
                item = ""
        else:
            item += character
    path_entries.append(item)

    first = True
    for path_entry in path_entries:
        # check for relative path entries (. and ..)
        if path_entry == "." or path_entry == "..":
            continue
        if first and path_entry.endswith(":"):
            # this is a windows drive letter, so make sure it's valid
            first = False
            if len(path_entry) != 2:
                status = ExecutionStatus.CONSTRAINT_FAILURE
                error_msg = ExecutionMessage(
                    message=f"The value {value} has an invalid drive specification.",
                    level=MessageLevel.ERROR,
                    source=source,
                    location=location,
                )
                messages.append(error_msg)
                return ExecutionResult(plugin_name, "Check file", status, messages)
            if (
                path_entry[0]
                not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            ):
                status = ExecutionStatus.CONSTRAINT_FAILURE
                error_msg = ExecutionMessage(
                    message=f"The value {value} has an invalid drive specification.",
                    level=MessageLevel.ERROR,
                    source=source,
                    location=location,
                )
                messages.append(error_msg)
                return ExecutionResult(plugin_name, "Check file", status, messages)
            continue
        else:
            # this needs to be a valid directory or file name
            for character in path_entry:
                if character not in valid_path_characters:
                    status = ExecutionStatus.CONSTRAINT_FAILURE
                    error_msg = ExecutionMessage(
                        message=f"The value {value} is not a valid file path.  Invalid character '{character}'.",
                        level=MessageLevel.ERROR,
                        source=source,
                        location=location,
                    )
                    messages.append(error_msg)
                    return ExecutionResult(plugin_name, "Check file", status, messages)

    # no bad content found, so return success
    return ExecutionResult(plugin_name, "Check file", status, messages)


def check_string(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check string constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    if not isinstance(value, str):
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"{value} is not a valid string value.  Type declaration = {type_declaration}",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check string", status, messages)


def check_int(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check int constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    is_invalid = False
    try:
        type_casted_int = int(value)
        # assert that the conversion didn't alter the contents, like in the case of float -> int.
        is_invalid = str(type_casted_int) != str(value)
    except Exception as error:
        is_invalid = True
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"AaC int primitive constraint failed for value {value} with error:{linesep}{error}",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    if is_invalid:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"{value} is not a valid value for the primitive type int",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check int", status, messages)


def check_number(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check number constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    is_invalid = False
    try:
        if isinstance(value, int):
            return ExecutionResult(plugin_name, "Check number", status, messages)
        if isinstance(value, float):
            return ExecutionResult(plugin_name, "Check number", status, messages)
        type_casted_float = float(value)
        # assert that the conversion didn't alter the contents, other than adding a '.0' for a whole number value.
        is_invalid = str(type_casted_float) != str(value) and str(
            type_casted_float
        ) != str(value + ".0")
    except Exception as error:
        is_invalid = True
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"AaC int primitive constraint failed for value {value} with error:{linesep}{error}",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    if is_invalid:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"{value} is not a valid value for the primitive type int",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check number", status, messages)


def check_dataref(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check dataref constraint."""

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    clean_value = str(value).strip()
    if clean_value.endswith("[]"):
        clean_value = value[:-2].strip()

    # get the dataref target from the parenthesis in the type_declaration
    dataref_target = type_declaration[
        type_declaration.find("(") + 1: type_declaration.find(")")
    ]
    if not dataref_target:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"Dataref constraint '{type_declaration}' failed for value '{clean_value}' with error: No dataref target provided.",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    context: LanguageContext = LanguageContext()
    found_values = context.get_values_by_field_chain(dataref_target)
    if clean_value not in found_values:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"Dataref constraint failed for value '{clean_value}': '{clean_value}' not found in '{dataref_target}' values '{found_values}'",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check dataref", status, messages)


def check_typeref(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check typeref constraint."""
    if not type_declaration.startswith("typeref"):
        raise Exception(
            f"Invalid typeref constraint: '{value}' for declaration '{type_declaration}' for source '{source.uri}' at location '{location}'"
        )

    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []

    clean_value = str(value).strip()
    if clean_value.endswith("[]"):
        clean_value = value[:-2].strip()

    if "(" in clean_value:
        clean_value = clean_value[: clean_value.find("(")].strip()

    context: LanguageContext = LanguageContext()

    qualified_type_name = type_declaration[
        type_declaration.find("(") + 1: type_declaration.find(")")
    ]
    parts = qualified_type_name.split(".")
    package_name = ".".join(parts[:-1])
    type_name = parts[-1]

    definitions_of_type = context.get_definitions_of_type(package_name, type_name)
    value_defining_type = context.get_definitions_by_name(clean_value)

    if len(value_defining_type) != 1:
        status = ExecutionStatus.CONSTRAINT_FAILURE
        error_msg = ExecutionMessage(
            message=f"Typeref constraint {type_declaration} failed for value {clean_value} with error: No unique defining schema found for value.",
            level=MessageLevel.ERROR,
            source=source,
            location=location,
        )
        messages.append(error_msg)
    else:
        value_root_key = value_defining_type[0].get_root_key()
        root_type_definition = context.get_defining_schema_for_root(value_root_key)
        if root_type_definition not in definitions_of_type:
            status = ExecutionStatus.CONSTRAINT_FAILURE
            error_msg = ExecutionMessage(
                message=f"Typeref constraint {type_declaration} failed for value {clean_value} with error: Value {clean_value} is not a valid {qualified_type_name}.",
                level=MessageLevel.ERROR,
                source=source,
                location=location,
            )
            messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check typeref", status, messages)
