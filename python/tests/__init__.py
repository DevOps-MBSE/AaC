import os

from functools import wraps
from tempfile import TemporaryDirectory


def _temporary_directory_enter(fn):

    @wraps(fn)
    def wrapper(td: TemporaryDirectory):
        return os.path.realpath(td.name)

    return wrapper


TemporaryDirectory.__enter__ = _temporary_directory_enter(TemporaryDirectory.__enter__)
