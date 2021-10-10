from setuptools import setup, find_packages

runtime_dependencies = [
    "attrs == 21.2.0",
    "coverage == 6.0",
    "jsonschema == 4.0.1",
    "pyrsistent == 0.18.0",
    "PyYAML == 5.4.1",
    "six == 1.16.0",
    "click == 8.0.1",
    "pathspec == 0.9.0",
    "platformdirs == 2.4.0",
    "pyrsistent == 0.18.0",
    "regex == 2021.9.30",
    "typing-extensions == 3.10.0.2",
    "pluggy == 1.0.0",
]

development_dependencies = [
    "flake8 == 3.9.2",
    "black == 21.9b0",
    "mccabe == 0.6.1",
    "mypy-extensions == 0.4.3",
    "pycodestyle == 2.7.0",
    "pyflakes == 2.3.1",
]

test_dependencies = ["nose2 == 0.10.0", "coverage == 6.0"]

setup(
    name="aac",
    version="3.0.0",
    packages=find_packages(where="aac", exclude="tests"),
    package_dir={"": "src"},
    install_requires=runtime_dependencies,
    setup_requires=development_dependencies,
    tests_require=test_dependencies,
    extras_require={
        "test": test_dependencies,
        "dev": development_dependencies,
        "all": test_dependencies + development_dependencies,
    },
)
