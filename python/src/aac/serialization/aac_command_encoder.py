"""Helpers for serializing an AaC command to JSON."""

from json import JSONEncoder

from aac.cli.aac_command import AacCommand, AacCommandArgument


class AacCommandArgumentEncoder(JSONEncoder):
    """Allow an AacCommandArgument to be JSON-encoded."""

    def default(self, object: AacCommandArgument):
        """Return a JSON-serializable version of an AaC command argument."""
        if isinstance(object, AacCommandArgument):
            return object.__dict__

        return JSONEncoder.default(self, object)


class AacCommandEncoder(JSONEncoder):
    """Allow an AacCommand to be JSON-encoded."""

    def default(self, object: AacCommand):
        """Return a JSON-serializable version of an AaC command."""
        if isinstance(object, AacCommand):
            arg_encoder = AacCommandArgumentEncoder()
            return {
                "name": object.name,
                "description": object.description,
                "arguments": [arg_encoder.default(arg) for arg in object.arguments],
            }

        return JSONEncoder.default(self, object)
