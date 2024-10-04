"""The Architecture-as-Code tool."""

# Run Python3.9 Check before continuing
import sys

if sys.version_info < (3, 9):
    minor = sys.version_info.minor
    major = sys.version_info.major
    print(f"Python version {major}.{minor} is too low; AaC requires at least Python version 3.9 or higher to run.")
    exit(1)

import logging
import os

__version__ = "0.4.28"

__log_file_name__ = os.path.join(os.path.dirname(__file__), "aac.log")

logging.basicConfig(
    format="%(asctime)s::%(pathname)s:%(lineno)d::%(levelname)s::%(message)s",
    filename=__log_file_name__,
    encoding="utf-8",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %H:%M:%S",
)

__all__ = ("__version__",)
