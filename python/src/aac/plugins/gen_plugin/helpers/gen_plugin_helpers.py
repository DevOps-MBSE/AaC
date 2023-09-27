def get_import_for_command(command_name: str) -> str:
    return f"from aac.plugins.{command_name} import {command_name}"