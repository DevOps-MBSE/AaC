from setuptools import setup

setup(
    version="0.0.1",
    name="aac-flair-echo",
    install_requires=["aac"],
    entry_points={
        "aac": ["aac-echo-flair=flair"],
    },
)
