from setuptools import setup

setup(
    version="0.0.1",
    name="jellyfish-flair-echo",
    install_requires="jellyfish",
    entry_points={
        "jellyfish": ["jellyfish-flair-echo=flair"],
    },
    py_modules=["flair"],
)
