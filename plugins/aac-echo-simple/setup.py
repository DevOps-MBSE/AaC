from setuptools import setup

setup(
    version="0.0.1",
    name="aac-echo-simple",
    install_requires=["aac"],
    entry_points={
        "aac": ["aac-echo-simple=simple"],
    },
)
