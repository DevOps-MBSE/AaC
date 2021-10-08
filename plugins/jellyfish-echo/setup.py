from setuptools import setup

setup(
    version="0.0.1",
    name="jellyfish-echo",
    install_requires="jellyfish",
    entry_points={
        "jellyfish": ["jellyfish-echo=echo"],
    },
    py_modules=["echo"],
)
