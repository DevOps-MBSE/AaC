import os

from functools import wraps
from tempfile import TemporaryDirectory


def _temporary_directory_init(fn):
    @wraps(fn)
    def wrapper(td: TemporaryDirectory, *args, **kwargs):
        fn(td, *args, **kwargs)
        td.name = os.path.realpath(td.name)

    return wrapper


def _temporary_directory_enter(fn):
    @wraps(fn)
    def wrapper(td: TemporaryDirectory):
        return os.path.realpath(td.name)

    return wrapper


TemporaryDirectory.__init__ = _temporary_directory_init(TemporaryDirectory.__init__)
TemporaryDirectory.__enter__ = _temporary_directory_enter(TemporaryDirectory.__enter__)
