"""Main entry point."""

import sys

if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "aac"


if __name__ == "__main__":
    from aac.cli.execute import cli

    cli()
