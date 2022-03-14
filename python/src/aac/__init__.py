"""The Architecture-as-Code tool."""
import logging

__version__ = "0.0.5"

logging.basicConfig(
    format="%(asctime)s::%(name)s::%(levelname)s::%(message)s",
    filename="aac.log",
    encoding="utf-8",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %H:%M:%S",
)
